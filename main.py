# -*- coding: utf-8 -*-
"""
Snake Daily Report - 每日焦點情報自動化主程式
專案入口調度核心：
1. 依指定模式（Copilot 365 自動化提問 或 即時 Direct 備援）收集 50 則主題最新資訊
2. 進行重複新聞過濾與字數合規檢核（同類新聞只保留一則，摘要限制 100 字內）
3. 透過 AI 摘要模組生成：今日三大重點、今日投資觀察、今日產業觀察、今日AI觀察與一句總結
4. 渲染產出現代科技風深色互動式 Dashboard (reports/YYYYMMDD.html)
5. 支援自動匯出高畫質 PDF 與 SMTP 電子郵件自動派送
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# 確保引用本專案目錄模組
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DATA_DIR, REPORTS_DIR, TOPIC_CATEGORIES
from summarizer import generate_ai_summary
from report_generator import render_html_dashboard
from exporter import export_html_to_pdf, send_email_report
from git_publisher import publish_to_github

def deduplicate_news(items: list) -> list:
    """
    資料清理與去重：
    1. 移除相同真實網址之新聞（排除通用搜尋引擎 fallback 網址）
    2. 比對標題相似度（文字重疊率 > 75% 視為重複），同類新聞只保留一則最具代表性者
    3. 強制確保摘要在 100 字以內
    """
    seen_urls = set()
    cleaned_items = []
    
    # 簡單文字相似度比對函式
    def is_similar(t1: str, t2: str) -> bool:
        s1 = set(t1.replace(" ", "").replace("，", "").replace("！", "").replace("？", ""))
        s2 = set(t2.replace(" ", "").replace("，", "").replace("！", "").replace("？", ""))
        if not s1 or not s2:
            return False
        overlap = len(s1 & s2)
        sim = overlap / min(len(s1), len(s2))
        return sim > 0.75

    for item in items:
        url = item.get("url", "").strip()
        title = item.get("title", "").strip()
        category = item.get("category", "")
        
        # 1. 網址去重（排除通用搜尋或預設 fallback 網址，避免同源 fallback 誤殺不同主題新聞）
        is_generic_url = any(u in url.lower() for u in ["bing.com/news", "google.com/search", "yahoo.com/news", "bing.com/search"])
        if url and not is_generic_url and url in seen_urls:
            continue
            
        # 2. 標題同類去重比對
        is_dup = False
        for kept in cleaned_items:
            if kept.get("category") == category:
                if is_similar(title, kept.get("title", "")):
                    is_dup = True
                    break
        if is_dup:
            continue

        # 3. 保留完整整理後摘要內容
        summary = item.get("summary", "").strip()
        item["summary"] = summary
            
        if url and not is_generic_url:
            seen_urls.add(url)
        cleaned_items.append(item)
        
    return cleaned_items

def run_pipeline(mode: str = "copilot", limit: int = 50, export_pdf: bool = True, send_email: bool = False, categories: list = None, publish_github: bool = True):
    """
    執行每日日報主流程
    """
    today_str = datetime.now().strftime("%Y%m%d")
    raw_data_file = DATA_DIR / f"raw_data_{today_str}.json"
    
    print("=" * 60)
    print(f" Snake Daily Report 每日情報自動化系統啟動 [{today_str}]")
    print(f" 執行模式: {mode.upper()} | 主題上限: {limit} 則 | 指定分類: {categories if categories else '全部'}")
    print("=" * 60)
    
    raw_items = []
    
    # --- [階段一：收集 50 則主題資訊] ---
    if mode == "copilot":
        print("\n[階段 1/4] 啟動 Microsoft 365 Copilot 視窗自動化問答...")
        try:
            from copilot_collector import collect_daily_topics_via_copilot
            raw_items = collect_daily_topics_via_copilot(limit=limit, resume=True, categories=categories)
        except Exception as e:
            print(f"[Copilot 自動化錯誤] {e}")
            print(">> 自動切換至 Direct 備援模式以確保日報順利生成...")
            from direct_collector import collect_daily_topics_direct
            raw_items = collect_daily_topics_direct(limit=limit, categories=categories)
    elif mode == "direct":
        print("\n[階段 1/4] 啟動 Direct 即時檢索收集模組...")
        from direct_collector import collect_daily_topics_direct
        raw_items = collect_daily_topics_direct(limit=limit, categories=categories)
    elif mode == "cache":
        print("\n[階段 1/4] 直接使用今日已暫存之數據檔案...")
        if raw_data_file.exists():
            with open(raw_data_file, "r", encoding="utf-8") as f:
                raw_items = json.load(f)
                if categories:
                    # 如果有指定分類，從快取中過濾
                    from config import TOPIC_CATEGORIES
                    valid_cat_names = [name for name, info in TOPIC_CATEGORIES.items() if info["code"] in categories]
                    raw_items = [item for item in raw_items if item.get("category") in valid_cat_names]
                raw_items = raw_items[:limit]
        else:
            print(f"[錯誤] 找不到快取檔案 {raw_data_file}，切換為 Direct 模式")
            from direct_collector import collect_daily_topics_direct
            raw_items = collect_daily_topics_direct(limit=limit, categories=categories)

    print(f"\n原始收集資訊共 {len(raw_items)} 則")

    # --- [階段二：去重與資料合規化] ---
    print("\n[階段 2/4] 執行資料去重與合規化審查...")
    processed_items = deduplicate_news(raw_items)
    print(f"去重完成，保留 {len(processed_items)} 則高價值獨家情報。")

    # --- [階段三：AI 智能摘要] ---
    print("\n[階段 3/4] 啟動 AI 智能歸納引擎生成今日觀察...")
    ai_summary = generate_ai_summary(processed_items)
    print(f" 今日一句總結：{ai_summary.get('punchline', '')}")

    # --- [階段四：產生 HTML 報告 Dashboard] ---
    print("\n[階段 4/4] 渲染現代科技風深色 HTML Dashboard...")
    html_path = render_html_dashboard(processed_items, ai_summary, today_str)

    # --- [附加加分功能：PDF 與 Email] ---
    pdf_path = None
    if export_pdf:
        print("\n[額外功能] 啟動 Microsoft Edge 轉檔為高品質 PDF...")
        pdf_path = export_html_to_pdf(html_path)

    if send_email:
        print("\n[額外功能] 啟動 Outlook 用戶端郵件自動派發...")
        send_email_report(html_path, pdf_path)

    if publish_github:
        print("\n[額外功能] 啟動 GitHub Pages 自動同步發布...")
        publish_to_github(html_path)

    print("\n" + "=" * 60)
    print(" 日報產出作業圓滿完成！")
    print(f" HTML Dashboard : {html_path}")
    if pdf_path:
        print(f" PDF 報告檔案   : {pdf_path}")
    print("=" * 60)
    return html_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Snake Daily Report - 每日焦點情報自動化系統")
    parser.add_argument("--mode", choices=["copilot", "direct", "cache"], default="copilot",
                        help="資料收集模式: copilot (預設，同視窗連續50問), direct (免介面即時備援), cache (讀取已存快取)")
    parser.add_argument("--limit", type=int, default=50,
                        help="限制處理的主題數量 (預設 50 則全部)")
    parser.add_argument("--categories", type=str, default="",
                        help="指定要收集的分類代碼 (A,B,C,D,E)，多個用逗號分隔，例如 A,C")
    parser.add_argument("--no-pdf", action="store_true",
                        help="關閉自動產出 PDF")
    parser.add_argument("--email", action="store_true",
                        help="啟動 Email 自動寄送")
    parser.add_argument("--no-github", action="store_true",
                        help="關閉自動發布至 GitHub")
    args = parser.parse_args()

    cat_list = [c.strip().upper() for c in args.categories.split(",")] if args.categories else None

    run_pipeline(
        mode=args.mode,
        limit=args.limit,
        export_pdf=not args.no_pdf,
        send_email=args.email,
        categories=cat_list,
        publish_github=not args.no_github
    )
