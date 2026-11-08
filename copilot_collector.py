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
from datetime import datetime, timedelta
from pathlib import Path

# 載入專案設定
from config import get_all_topics, COPILOT_PROMPT_TEMPLATE, DATA_DIR, NEWS_MAX_AGE_DAYS
from item_quality import is_fallback_item

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

    # 4. 缺少的欄位留空或如實標示，不填入看似真實的內容
    category = cat if cat else default_cat
    is_unparsed = not title
    if not title:
        title = f"{topic_name}：回覆無法解析"
    if not summary:
        summary = clean_text[:120] if len(clean_text) > 120 else clean_text
    if not source:
        source = "未標示來源"

    # 清理連結中的額外括號
    link = re.sub(r"[()（）\[\]]", "", link or "").strip()
    if not link.startswith("http"):
        link = ""

    return {
        "title": title,
        "summary": summary,
        "source": source,
        "publish_time": pub_time or "",
        "url": link,
        "category": category,
        "topic": topic_name,
        "raw_content": raw_text,
        "is_fallback": is_unparsed
    }

def _build_missing_item(topic_info: dict) -> dict:
    """建立明確標示為未取得的項目，下次執行時會重新提問"""
    topic_name = topic_info["topic"]
    return {
        "id": topic_info["id"],
        "title": f"{topic_name}：本次未取得資料",
        "summary": "Copilot 在等待時間內沒有回覆，重新執行時會自動重試。",
        "source": "系統標記",
        "publish_time": "",
        "url": "",
        "category": topic_info["category"],
        "topic": topic_name,
        "raw_content": "",
        "is_fallback": True
    }

def _save_cache(cache_file: Path, results: list):
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

# --- [Copilot 問答] ---
def _connect_copilot():
    """找到並激活 Copilot 視窗，回傳 (hwnd, UIA 視窗物件)"""
    hwnd = find_copilot_window()
    if not hwnd:
        raise RuntimeError("未偵測到正在執行的 Microsoft 365 Copilot 應用程式視窗！請先啟動 Copilot 365。")

    print(f"[連線成功] 找到 Copilot 視窗 HWND: {hwnd}")
    activate_window(hwnd)
    time.sleep(1.0)
    return hwnd, Desktop(backend="uia").window(handle=hwnd)

def _ask_copilot(hwnd, main_window, prompt: str, is_valid, timeout: int = 120):
    """送出提問並輪詢最新回覆；通過 is_valid 檢驗才回傳，逾時回傳 None"""
    activate_window(hwnd)
    focus_input_area(main_window)

    pyperclip.copy(prompt)
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)
    pyautogui.press("enter")

    # 發送後立即清空剪貼簿
    pyperclip.copy("")
    print(" -> 已送出提示詞，等待 Copilot 搜尋與生成回覆...")

    start_wait = time.time()
    time.sleep(8)  # 搜尋及初次打字緩衝

    while time.time() - start_wait < timeout:
        try:
            buttons = main_window.descendants(control_type="Button", title="複製回應")
            if not buttons:
                buttons = [b for b in main_window.descendants(control_type="Button") if "複製" in b.window_text()]

            if buttons:
                # 點擊最新的複製按鈕
                buttons[-1].invoke()
                time.sleep(0.5)
                clip_text = pyperclip.paste().strip()
                if clip_text and is_valid(clip_text):
                    return clip_text
        except Exception:
            pass
        time.sleep(2.5)
    return None

def ask_copilot_once(prompt: str, is_valid, timeout: int = 240):
    """在目前的 Copilot 聊天室追加一題，供每日分析使用"""
    hwnd, main_window = _connect_copilot()
    return _ask_copilot(hwnd, main_window, prompt, is_valid, timeout=timeout)

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
    
    # 檢查是否已有暫存數據 (斷點續傳)；未取得的備援項目不算完成，這次會重新提問
    if resume and cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                collected_results = [item for item in json.load(f) if not is_fallback_item(item)]
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

    hwnd, main_window = _connect_copilot()

    now = datetime.now()
    today_label = now.strftime("%Y-%m-%d")
    cutoff_label = (now - timedelta(days=NEWS_MAX_AGE_DAYS)).strftime("%Y-%m-%d")

    last_saved_text = ""
    if collected_results:
        last_saved_text = collected_results[-1].get("raw_content", "")

    def ask_topic(topic_info: dict):
        """提問一個主題；成功時解析並寫入快取，回傳是否成功"""
        nonlocal last_saved_text
        topic_name = topic_info["topic"]
        cat_name = topic_info["category"]
        prompt = COPILOT_PROMPT_TEMPLATE.format(
            topic=topic_name,
            category=cat_name,
            today=today_label,
            cutoff=cutoff_label
        )

        def is_valid_reply(text: str) -> bool:
            # 回覆必須提到本題主題，避免上一題的回覆被誤認為本題答案
            return (
                len(text) > 30
                and text != last_saved_text
                and "請搜尋並提供" not in text
                and topic_name in text
            )

        captured_text = _ask_copilot(hwnd, main_window, prompt, is_valid_reply)
        if not captured_text:
            print(" [逾時提醒] 120 秒內未取得有效回覆")
            return False

        last_saved_text = captured_text
        parsed_item = parse_copilot_response(captured_text, cat_name, topic_name)
        parsed_item["id"] = topic_info["id"]
        collected_results.append(parsed_item)

        # 即時寫入快取檔
        _save_cache(cache_file, collected_results)
        print(f"  完成：{parsed_item['title']}（來源：{parsed_item['source']}）")
        time.sleep(1.5)  # 輪次微幅間隔，維持穩定度
        return True

    total_to_run = len(remaining_topics)
    print(f"[開始執行] 即將在同一個聊天室中依序處理 {total_to_run} 則主題問答...")

    failed_topics = []
    for i, topic_info in enumerate(remaining_topics, 1):
        print(f"\n[{i}/{total_to_run}] (總進度 No.{topic_info['id']}/50) 正在查詢【{topic_info['category']}】: {topic_info['topic']}")
        if not ask_topic(topic_info):
            failed_topics.append(topic_info)

    # 全部問完後，逾時的主題再問一次
    if failed_topics:
        print(f"\n[重試] 共 {len(failed_topics)} 則主題未取得回覆，重新提問一次...")
        still_failed = []
        for topic_info in failed_topics:
            print(f"\n[重試] 【{topic_info['category']}】: {topic_info['topic']}")
            if not ask_topic(topic_info):
                still_failed.append(topic_info)
        for topic_info in still_failed:
            collected_results.append(_build_missing_item(topic_info))

    collected_results.sort(key=lambda item: item.get("id", 0))
    _save_cache(cache_file, collected_results)

    missing_count = sum(1 for item in collected_results if item.get("is_fallback"))
    print(f"\n[收集完成] 成功 {len(collected_results) - missing_count} 則，未取得 {missing_count} 則，快取已存至：{cache_file}")
    return collected_results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Copilot 365 自動化收集測試")
    parser.add_argument("--limit", type=int, default=2, help="測試收集的題目數量 (預設 2 題)")
    parser.add_argument("--test-analysis", action="store_true", help="只用最新一份快取測試每日分析題")
    args = parser.parse_args()
    
    if args.test_analysis:
        from item_quality import annotate_items
        from summarizer import generate_copilot_analysis

        latest_file = sorted(DATA_DIR.glob("raw_data_*.json"))[-1]
        report_date = latest_file.stem.rsplit("_", 1)[-1]
        with open(latest_file, "r", encoding="utf-8") as f:
            items = annotate_items(json.load(f), report_date)
        print(f"=== 測試每日分析題：{latest_file.name} ===")
        result = generate_copilot_analysis(items, report_date)
        print(json.dumps(result, ensure_ascii=False, indent=2) if result else "未取得可用的分析結果")
        sys.exit(0)

    print("=== 測試啟動 Copilot 365 收集模組 ===")
    res = collect_daily_topics_via_copilot(limit=args.limit)
    print(f"成功收集 {len(res)} 則資料：")
    for r in res:
        print(f"- [{r['category']}] {r['title']}: {r['summary']}")
