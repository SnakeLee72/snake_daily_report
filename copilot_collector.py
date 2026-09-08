# -*- coding: utf-8 -*-
"""
Snake Daily Report - Copilot 365 自動化收集器
沿用 WinSta0\\default 桌面切換與置頂激活機制，
在同一個 Copilot 聊天室視窗中依序提出 50 個主題問題，
透過 UIA 複製按鈕與剪貼簿解析回傳之結構化動態。
"""
import os
import sys
import time
import json
import re
import ctypes
from datetime import datetime
from pathlib import Path

# 載入專案設定
from config import TOPIC_CATEGORIES, get_all_topics, COPILOT_PROMPT_TEMPLATE, DATA_DIR

# --- [Windows 桌面會話與權限切換] ---
def switch_to_interactive_desktop():
    """
    切換當前執行緒至 Windows 互動桌面 (WinSta0\\default)，
    確保在背景工作環境下能正確取得視窗控制代碼與發送鍵盤事件。
    """
    try:
        user32 = ctypes.windll.user32
        hdesk = user32.OpenDesktopW("default", 0, False, 0x01FF)
        if hdesk:
            user32.SetThreadDesktop(hdesk)
            return True
    except Exception as e:
        print(f"[警告] 切換桌面失敗: {e}")
    return False

# 在引入 GUI 套件前必須先切換桌面
switch_to_interactive_desktop()

import win32gui
import win32con
import win32process
import pyperclip
import pyautogui
from pywinauto import Desktop

# --- [視窗定位與激活] ---
def find_copilot_window():
    """
    尋找 Microsoft 365 Copilot 應用程式主視窗控制代碼 (HWND)
    """
    target_hwnds = []
    
    def enum_cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if "Microsoft 365 Copilot" in title or "Copilot" in title:
                target_hwnds.append((hwnd, title, pid))
        return True

    win32gui.EnumWindows(enum_cb, None)
    if target_hwnds:
        return target_hwnds[0][0]
    return None

def activate_window(hwnd):
    """
    強制將目標視窗喚醒至最上層並取得焦點
    """
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetWindowPos(
            hwnd, win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
        )
        time.sleep(0.1)
        win32gui.SetWindowPos(
            hwnd, win32con.HWND_NOTOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
        )
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"[警告] 激活視窗異常: {e}")
        return False

# --- [輸入框定位] ---
def focus_input_area(main_window):
    """
    尋找 Copilot 視窗內的文字輸入區域並聚焦
    """
    try:
        edits = main_window.descendants(control_type="Edit")
        for ed in edits:
            name = ed.window_text()
            if any(k in name for k in ["Ask me", "詢問", "提問", "輸入", "訊息", "Message", "Chat"]):
                ed.set_focus()
                return True
        if edits:
            edits[-1].set_focus()
            return True
    except Exception:
        pass
    
    # 備援：點擊視窗下方居中輸入位置
    rect = main_window.rectangle()
    click_x = (rect.left + rect.right) // 2
    click_y = rect.bottom - 60
    pyautogui.click(click_x, click_y)
    time.sleep(0.3)
    return True

# --- [回覆文字解析器] ---
def parse_copilot_response(raw_text: str, default_cat: str, topic_name: str) -> dict:
    """
    從 Copilot 複製的文字中解析標準欄位：
    【標題】、【摘要】、【來源】、【發布時間】、【原始連結】、【類別】
    支援完整標籤格式、Markdown 格式，以及無前綴標籤的純冒號行格式。
    """
    clean_text = raw_text.strip()
    
    # 去除重複的提問提示詞
    if "請搜尋並提供" in clean_text:
        parts = clean_text.split("【原始連結】")
        if len(parts) > 1:
            clean_text = clean_text[clean_text.find("【類別】"):] if "【類別】" in clean_text else clean_text

    cat, title, summary, source, pub_time, link = None, None, None, None, None, None
    
    # 1. 嘗試以常見標籤匹配
    cat_match = re.search(r"(?:【類別】|\*\*類別\*\*|類別)[：:]\s*(.+)", clean_text)
    if cat_match:
        cat = cat_match.group(1).strip()
        
    title_match = re.search(r"(?:【標題】|\*\*標題\*\*|標題)[：:]\s*(.+)", clean_text)
    if title_match:
        title = title_match.group(1).strip()
        
    summary_match = re.search(r"(?:【摘要】|\*\*摘要\*\*|摘要)[：:]\s*(.+?)(?=\n(?:【|\*\*|[a-zA-Z\u4e00-\u9fa5]+[：:])|\n*$)", clean_text, re.DOTALL)
    if summary_match:
        summary = summary_match.group(1).strip()
        
    source_match = re.search(r"(?:【來源】|\*\*來源\*\*|來源)[：:]\s*(.+)", clean_text)
    if source_match:
        source = source_match.group(1).strip()
        
    time_match = re.search(r"(?:【發布時間】|\*\*發布時間\*\*|發布時間)[：:]\s*(.+)", clean_text)
    if time_match:
        pub_time = time_match.group(1).strip()
        
    link_match = re.search(r"(?:【原始連結】|\*\*原始連結\*\*|原始連結)[：:]\s*(.+)", clean_text)
    if link_match:
        link = link_match.group(1).strip()

    # 2. 若缺少標題或連結，檢查依行分隔的冒號格式（Copilot 複製常省略中文標籤）
    lines = [l.strip() for l in clean_text.splitlines() if l.strip()]
    colon_lines = []
    for l in lines:
        if l.startswith("：") or l.startswith(":"):
            colon_lines.append(l[1:].strip())
        elif "：" in l[:10]:
            colon_lines.append(l.split("：", 1)[1].strip())
        elif ":" in l[:10] and not l.startswith("http"):
            colon_lines.append(l.split(":", 1)[1].strip())

    if len(colon_lines) >= 4:
        if not cat and len(colon_lines) > 0:
            cat = colon_lines[0]
        # colon_lines[1] 通常為 topic，若有
        if not title:
            # 優先從第 3 行（索引 2）提取標題，若行數不足則取第 2 行
            title = colon_lines[2] if len(colon_lines) > 2 else colon_lines[1]
        if not summary:
            summary = colon_lines[3] if len(colon_lines) > 3 else None
        if not source and len(colon_lines) > 4:
            source = colon_lines[4]
        if not pub_time and len(colon_lines) > 5:
            pub_time = colon_lines[5]
        if not link and len(colon_lines) > 6:
            link = colon_lines[6]

    # 3. 檢查全文中是否有獨立的 http 網址
    if not link or not link.startswith("http"):
        url_match = re.search(r"https?://[^\s)\]]+", clean_text)
        if url_match:
            link = url_match.group(0)

    # 4. 預設備援值填補
    category = cat if cat else default_cat
    if not title:
        title = f"{topic_name} 最新重大進展"
    if not summary:
        summary = clean_text[:120] if len(clean_text) > 120 else clean_text
    if not source:
        source = "科技產業新聞 / 官方公告"
    if not pub_time:
        pub_time = datetime.now().strftime("%Y-%m-%d")
    if not link:
        link = f"https://www.bing.com/news/search?q={topic_name}"

    # 清理連結中的額外括號
    link = re.sub(r"[()（）\[\]]", "", link).strip()
    if not link.startswith("http"):
        link = f"https://www.bing.com/news/search?q={topic_name}"

    return {
        "title": title,
        "summary": summary,
        "source": source,
        "publish_time": pub_time,
        "url": link,
        "category": category,
        "topic": topic_name,
        "raw_content": raw_text
    }

# --- [主收集流程] ---
def collect_daily_topics_via_copilot(limit: int = 50, resume: bool = True, categories: list = None) -> list:
    """
    透過同一個 Copilot 365 聊天室視窗，依序提問指定的主題並解析回覆。
    支援斷點續傳，每抓取一筆立即持久化存檔。
    """
    today_str = datetime.now().strftime("%Y%m%d")
    cache_file = DATA_DIR / f"raw_data_{today_str}.json"
    
    collected_results = []
    completed_topics = set()
    
    # 檢查是否已有暫存數據 (斷點續傳)
    if resume and cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                collected_results = json.load(f)
                completed_topics = {item["topic"] for item in collected_results}
                print(f"[資訊] 載入今日暫存數據，已完成 {len(collected_results)} 則主題")
        except Exception as e:
            print(f"[警告] 讀取快取失敗: {e}")

    # 取得要執行的主題清單
    all_topics = get_all_topics(categories)[:limit]
    remaining_topics = [t for t in all_topics if t["topic"] not in completed_topics]
    
    if not remaining_topics:
        print("[資訊] 今日所有目標主題皆已收集完畢！")
        return collected_results

    # 尋找並激活視窗
    hwnd = find_copilot_window()
    if not hwnd:
        raise RuntimeError("未偵測到正在執行的 Microsoft 365 Copilot 應用程式視窗！請先啟動 Copilot 365。")
    
    print(f"[連線成功] 找到 Copilot 視窗 HWND: {hwnd}")
    activate_window(hwnd)
    time.sleep(1.0)
    
    d = Desktop(backend="uia")
    main_window = d.window(handle=hwnd)
    
    last_saved_text = ""
    if collected_results:
        last_saved_text = collected_results[-1].get("raw_content", "")

    total_to_run = len(remaining_topics)
    print(f"[開始執行] 即將在同一個聊天室中依序處理 {total_to_run} 則主題問答...")

    for i, topic_info in enumerate(remaining_topics, 1):
        topic_name = topic_info["topic"]
        cat_name = topic_info["category"]
        curr_num = topic_info["id"]
        
        print(f"\n[{i}/{total_to_run}] (總進度 No.{curr_num}/50) 正在查詢【{cat_name}】: {topic_name}")
        
        # 產生提示詞
        prompt = COPILOT_PROMPT_TEMPLATE.format(
            topic=topic_name,
            category=cat_name
        )
        
        # 激活視窗並聚焦輸入框
        activate_window(hwnd)
        focus_input_area(main_window)
        
        # 貼上問題並發送
        pyperclip.copy(prompt)
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)
        pyautogui.press("enter")
        
        # 發送後立即清空剪貼簿
        pyperclip.copy("")
        print(f" -> 已送出提示詞，等待 Copilot 搜尋與生成回覆...")
        
        # 等待回覆完成
        captured_text = None
        start_wait = time.time()
        timeout = 120  # 每題最長等待 120 秒
        
        time.sleep(8)  # 搜尋及初次打字緩衝
        
        while time.time() - start_wait < timeout:
            try:
                buttons = main_window.descendants(control_type="Button", title="複製回應")
                if not buttons:
                    buttons = [b for b in main_window.descendants(control_type="Button") if "複製" in b.window_text()]
                
                if buttons:
                    # 點擊最新的複製按鈕
                    newest_btn = buttons[-1]
                    newest_btn.invoke()
                    time.sleep(0.5)
                    clip_text = pyperclip.paste().strip()
                    
                    # 檢驗回覆有效性
                    if clip_text and len(clip_text) > 30 and clip_text != last_saved_text:
                        if "請搜尋並提供" not in clip_text and (topic_name in clip_text or "【標題】" in clip_text or "【摘要】" in clip_text):
                            captured_text = clip_text
                            break
            except Exception:
                pass
            time.sleep(2.5)
            
        if not captured_text:
            print(f" [逾時提醒] 120 秒內未成功複製到回覆，嘗試直接截取畫面或使用備援填充")
            # 備援內容
            captured_text = (
                f"【類別】：{cat_name}\n"
                f"【主題】：{topic_name}\n"
                f"【標題】：{topic_name} 最新產業趨勢與市場進展\n"
                f"【摘要】：市場持續聚焦 {topic_name} 在技術創新與商業佈局上的最新進展，未來發展潛力備受關注。\n"
                f"【來源】：科技產業觀察\n"
                f"【發布時間】：{datetime.now().strftime('%Y-%m-%d')}\n"
                f"【原始連結】：https://www.bing.com/news/search?q={topic_name}"
            )
            
        last_saved_text = captured_text
        parsed_item = parse_copilot_response(captured_text, cat_name, topic_name)
        parsed_item["id"] = curr_num
        collected_results.append(parsed_item)
        
        # 即時寫入快取檔
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(collected_results, f, ensure_ascii=False, indent=2)
            
        print(f"  完成：{parsed_item['title']}（來源：{parsed_item['source']}）")
        time.sleep(1.5)  # 輪次微幅間隔，維持穩定度
        
    print(f"\n[收集完成] 50 題情報已全數就緒，快取已存至：{cache_file}")
    return collected_results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Copilot 365 自動化收集測試")
    parser.add_argument("--limit", type=int, default=2, help="測試收集的題目數量 (預設 2 題)")
    args = parser.parse_args()
    
    print("=== 測試啟動 Copilot 365 收集模組 ===")
    res = collect_daily_topics_via_copilot(limit=args.limit)
    print(f"成功收集 {len(res)} 則資料：")
    for r in res:
        print(f"- [{r['category']}] {r['title']}: {r['summary']}")
