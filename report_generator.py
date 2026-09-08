import os
import json
from datetime import datetime
from pathlib import Path
from config import REPORTS_DIR, TOPIC_CATEGORIES

def render_html_dashboard(news_items: list, ai_summary: dict, target_date: str = None) -> Path:
    """
    將新聞與 AI 摘要渲染為完整獨立的 HTML Dashboard 檔案
    """
    if not target_date:
        target_date = datetime.now().strftime("%Y%m%d")
        
    display_date = f"{target_date[:4]}年{target_date[4:6]}月{target_date[6:]}日"
    now_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 統計各類別數量
    category_counts = {}
    for cat in TOPIC_CATEGORIES.keys():
        category_counts[cat] = 0
    for item in news_items:
        cat = item.get("category", "其他")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
    total_count = len(news_items)
    
    # 選出 TOP 10 重點新聞（依序優先取各類首選與重要權值）
    top10_items = []
    seen_ids = set()
    for cat_name in TOPIC_CATEGORIES.keys():
        cat_items = [x for x in news_items if x.get("category") == cat_name]
        for it in cat_items[:2]:
            if it.get("id") not in seen_ids:
                top10_items.append(it)
                seen_ids.add(it.get("id"))
    for it in news_items:
        if len(top10_items) >= 10:
            break
        if it.get("id") not in seen_ids:
            top10_items.append(it)
            seen_ids.add(it.get("id"))
            
    # 組裝 AI 摘要內容
    top_three_html = "".join([f"<li><span class='bullet-badge'>{i+1}</span> {point}</li>" for i, point in enumerate(ai_summary.get("top_three", []))])
    inv_obs = ai_summary.get("investment_observation", "")
    ind_obs = ai_summary.get("industry_observation", "")
    ai_obs = ai_summary.get("ai_observation", "")
    punchline = ai_summary.get("punchline", "科技浪潮全面步入新紀元。")

    # 組裝五大分類的卡片 HTML
    sections_html = ""
    for cat_name, cat_meta in TOPIC_CATEGORIES.items():
        cat_items = [x for x in news_items if x.get("category") == cat_name]
        cat_icon = cat_meta.get("icon", "📌")
        cat_color = cat_meta.get("color", "#38bdf8")
        
        cards_html = ""
        for it in cat_items:
            cards_html += f'''
            <div class="news-card" data-category="{cat_name}" data-title="{it.get('title', '')}" data-topic="{it.get('topic', '')}">
                <div class="card-header">
                    <span class="topic-tag" style="background-color: {cat_color}22; color: {cat_color}; border: 1px solid {cat_color}55;">
                        {it.get('topic')}
                    </span>
                    <span class="pub-time">{it.get('publish_time')}</span>
                </div>
                <h4 class="card-title">{it.get('title')}</h4>
                <p class="card-summary">{it.get('summary')}</p>
                <div class="card-footer">
                    <span class="source-tag">🏷️ {it.get('source')}</span>
                    <a href="{it.get('url')}" target="_blank" rel="noopener noreferrer" class="link-btn">
                        點擊開啟原文 ↗
                    </a>
                </div>
            </div>
            '''
            
        sections_html += f'''
        <section class="category-section" id="section-{cat_meta['code']}" data-category="{cat_name}">
            <div class="section-header" onclick="toggleSection('{cat_meta['code']}')">
                <div class="section-header-left">
                    <span class="section-icon">{cat_icon}</span>
                    <h3 class="section-title">{cat_name}動態</h3>
                    <span class="section-count-badge" style="background-color: {cat_color}22; color: {cat_color};">
                        {len(cat_items)} 則
                    </span>
                </div>
                <div class="section-header-right">
                    <span class="toggle-arrow" id="arrow-{cat_meta['code']}">▼</span>
                </div>
            </div>
            <div class="section-body" id="body-{cat_meta['code']}">
                <div class="news-grid">
                    {cards_html}
                </div>
            </div>
        </section>
        '''

    # TOP 10 卡片 HTML
    top10_html = ""
    for idx, it in enumerate(top10_items, 1):
        cat = it.get("category", "其他")
        cat_color = TOPIC_CATEGORIES.get(cat, {}).get("color", "#38bdf8")
        top10_html += f'''
        <div class="top10-card">
            <div class="top10-rank" style="color: {cat_color};">#{idx:02d}</div>
            <div class="top10-content">
                <div class="top10-meta">
                    <span class="badge" style="background: {cat_color}22; color: {cat_color};">{cat} · {it.get('topic')}</span>
                    <span class="time">{it.get('publish_time')}</span>
                </div>
                <h4 class="top10-title">{it.get('title')}</h4>
                <p class="top10-summary">{it.get('summary')}</p>
                <div class="top10-footer">
                    <span class="source">來源：{it.get('source')}</span>
                    <a href="{it.get('url')}" target="_blank" rel="noopener noreferrer" class="top10-link">開啟原文 ↗</a>
                </div>
            </div>
        </div>
        '''

    # 動態產生篩選標籤
    filter_tabs_html = f'<button class="tab-btn active" data-category="all" onclick="filterCategory(\'all\', this)">全部 ({total_count})</button>'
    for cat_name, cat_meta in TOPIC_CATEGORIES.items():
        filter_tabs_html += f'\n                <button class="tab-btn" data-category="{cat_name}" onclick="filterCategory(\'{cat_name}\', this)">{cat_name} ({category_counts.get(cat_name, 0)})</button>'

    # 動態產生統計看板
    stats_bar_html = ""
    for cat_name, cat_meta in TOPIC_CATEGORIES.items():
        code = cat_meta["code"]
        icon = cat_meta.get("icon", "📌")
        stats_bar_html += f'''
            <div class="stat-card" onclick="scrollToSection('{code}')">
                <div class="stat-info">
                    <div class="stat-name">{cat_name}</div>
                    <div class="stat-num">{category_counts.get(cat_name, 0)}</div>
                </div>
                <div class="stat-icon">{icon}</div>
            </div>'''

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snake Daily Report - {display_date}</title>
    <style>
        :root {{
            --bg-main: #0a0f1d;
            --bg-card: rgba(18, 25, 44, 0.75);
            --bg-card-hover: rgba(28, 39, 68, 0.9);
            --border-color: rgba(56, 189, 248, 0.15);
            --border-hover: rgba(56, 189, 248, 0.4);
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --accent-cyan: #38bdf8;
            --accent-purple: #818cf8;
            --accent-green: #34d399;
            --accent-pink: #f472b6;
            --accent-amber: #fbbf24;
            --radius-lg: 16px;
            --radius-md: 10px;
            --radius-sm: 6px;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans TC", "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-main);
            color: var(--text-main);
            line-height: 1.6;
            padding-bottom: 60px;
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 85% 75%, rgba(129, 140, 248, 0.08) 0%, transparent 40%);
            min-height: 100vh;
        }}

        .container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 24px 20px;
        }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 28px;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            margin-bottom: 24px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            position: relative;
            overflow: hidden;
        }}
        .header::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(to bottom, var(--accent-cyan), var(--accent-purple));
        }}
        .header-title-area h1 {{
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(to right, #ffffff, var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }}
        .header-meta {{
            color: var(--text-muted);
            font-size: 14px;
            display: flex;
            gap: 16px;
            align-items: center;
        }}
        .header-actions {{
            display: flex;
            gap: 12px;
        }}
        .btn {{
            padding: 10px 18px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            background: rgba(30, 41, 59, 0.7);
            color: var(--text-main);
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .btn:hover {{
            background: var(--accent-cyan);
            color: #0b0f19;
            border-color: var(--accent-cyan);
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        }}

        .toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 24px;
            padding: 16px 20px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
        }}
        .search-box {{
            flex: 1;
            min-width: 260px;
            position: relative;
        }}
        .search-input {{
            width: 100%;
            padding: 10px 16px 10px 38px;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            color: var(--text-main);
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-input:focus {{
            border-color: var(--accent-cyan);
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
        }}
        .search-icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            font-size: 14px;
        }}
        .filter-tabs {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .tab-btn {{
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            border: 1px solid var(--border-color);
            background: transparent;
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.2s;
        }}
        .tab-btn.active, .tab-btn:hover {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent-cyan);
            border-color: var(--accent-cyan);
        }}

        .ai-summary-container {{
            background: linear-gradient(135deg, rgba(20, 27, 45, 0.85), rgba(15, 23, 42, 0.95));
            border: 1px solid rgba(129, 140, 248, 0.3);
            border-radius: var(--radius-lg);
            padding: 24px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            position: relative;
        }}
        .ai-summary-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 12px;
        }}
        .ai-badge {{
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
            color: #0b0f19;
            font-size: 12px;
            font-weight: 800;
            padding: 4px 10px;
            border-radius: 12px;
        }}
        .ai-summary-title {{
            font-size: 20px;
            font-weight: 700;
            color: #fff;
        }}
        .punchline-card {{
            background: rgba(56, 189, 248, 0.08);
            border-left: 4px solid var(--accent-cyan);
            padding: 14px 18px;
            border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
            font-size: 16px;
            font-weight: 600;
            color: #e2e8f0;
            margin-bottom: 20px;
        }}
        .ai-summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 18px;
        }}
        .summary-card {{
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: var(--radius-md);
            padding: 18px;
        }}
        .summary-card-title {{
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .summary-card p {{
            font-size: 14px;
            color: var(--text-muted);
            line-height: 1.6;
        }}
        .top-three-list {{
            list-style: none;
        }}
        .top-three-list li {{
            font-size: 14px;
            color: var(--text-muted);
            margin-bottom: 8px;
            display: flex;
            align-items: flex-start;
            gap: 8px;
        }}
        .bullet-badge {{
            background: rgba(56, 189, 248, 0.2);
            color: var(--accent-cyan);
            font-weight: 700;
            font-size: 11px;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            margin-top: 2px;
        }}

        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
            border-color: var(--border-hover);
        }}
        .stat-info .stat-name {{
            font-size: 13px;
            color: var(--text-muted);
        }}
        .stat-info .stat-num {{
            font-size: 22px;
            font-weight: 700;
            color: #fff;
        }}
        .stat-icon {{
            font-size: 26px;
            opacity: 0.8;
        }}

        .top10-section {{
            margin-bottom: 36px;
        }}
        .top10-header {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
            color: #fff;
        }}
        .top10-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 16px;
        }}
        .top10-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 16px;
            display: flex;
            gap: 14px;
            transition: all 0.2s;
        }}
        .top10-card:hover {{
            background: var(--bg-card-hover);
            border-color: var(--accent-cyan);
            transform: translateY(-2px);
        }}
        .top10-rank {{
            font-size: 24px;
            font-weight: 900;
            font-family: monospace;
            line-height: 1;
        }}
        .top10-content {{
            flex: 1;
        }}
        .top10-meta {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            margin-bottom: 6px;
        }}
        .top10-meta .badge {{
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 600;
        }}
        .top10-meta .time {{
            color: var(--text-muted);
        }}
        .top10-title {{
            font-size: 15px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 6px;
            line-height: 1.4;
        }}
        .top10-summary {{
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 10px;
            line-height: 1.5;
        }}
        .top10-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: var(--text-muted);
        }}
        .top10-link {{
            color: var(--accent-cyan);
            text-decoration: none;
            font-weight: 600;
        }}
        .top10-link:hover {{
            text-decoration: underline;
        }}

        .category-section {{
            margin-bottom: 24px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            overflow: hidden;
            transition: border-color 0.2s;
        }}
        .section-header {{
            padding: 18px 24px;
            background: rgba(15, 23, 42, 0.6);
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
            border-bottom: 1px solid transparent;
            transition: background-color 0.2s;
        }}
        .section-header:hover {{
            background: rgba(30, 41, 59, 0.6);
        }}
        .section-header-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .section-icon {{
            font-size: 22px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: #fff;
        }}
        .section-count-badge {{
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 700;
        }}
        .toggle-arrow {{
            color: var(--text-muted);
            font-size: 14px;
            transition: transform 0.3s;
        }}
        .toggle-arrow.collapsed {{
            transform: rotate(-90deg);
        }}
        .section-body {{
            padding: 20px;
            display: block;
        }}
        .section-body.collapsed {{
            display: none;
        }}

        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 18px;
        }}
        .news-card {{
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: var(--radius-md);
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.2s;
        }}
        .news-card:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-hover);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .topic-tag {{
            font-size: 12px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: var(--radius-sm);
        }}
        .pub-time {{
            font-size: 12px;
            color: var(--text-muted);
        }}
        .card-title {{
            font-size: 15px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 8px;
            line-height: 1.45;
        }}
        .card-summary {{
            font-size: 13px;
            color: #cbd5e1;
            line-height: 1.55;
            margin-bottom: 14px;
            flex-grow: 1;
        }}
        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            padding-top: 10px;
            font-size: 12px;
        }}
        .source-tag {{
            color: var(--text-muted);
            max-width: 150px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .link-btn {{
            color: var(--accent-cyan);
            text-decoration: none;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 3px;
            transition: color 0.2s;
        }}
        .link-btn:hover {{
            color: #fff;
            text-decoration: underline;
        }}

        @media print {{
            body {{
                background: #fff !important;
                color: #000 !important;
                background-image: none !important;
            }}
            .header, .ai-summary-container, .top10-card, .category-section, .news-card {{
                background: #fff !important;
                border: 1px solid #ccc !important;
                box-shadow: none !important;
                color: #000 !important;
                break-inside: avoid;
            }}
            .header-title-area h1 {{
                -webkit-text-fill-color: #000 !important;
                color: #000 !important;
            }}
            .toolbar, .header-actions, .toggle-arrow {{
                display: none !important;
            }}
            .card-title, .top10-title, .ai-summary-title {{
                color: #000 !important;
            }}
            .card-summary, .top10-summary, p {{
                color: #333 !important;
            }}
            .section-body {{
                display: block !important;
            }}
        }}

        @media (max-width: 768px) {{
            .header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 16px;
            }}
            .header-actions {{
                width: 100%;
                justify-content: flex-start;
            }}
            .toolbar {{
                flex-direction: column;
                align-items: stretch;
            }}
            .filter-tabs {{
                overflow-x: auto;
                padding-bottom: 6px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 主頁首部 Header -->
        <header class="header">
            <div class="header-title-area">
                <h1>Snake Daily Report</h1>
                <div class="header-meta">
                    <span>📅 {display_date}</span>
                    <span>🕒 報告產生時間：{now_time_str}</span>
                    <span>📊 收錄資訊：共 {total_count} 則</span>
                </div>
            </div>
            <div class="header-actions">
                <button class="btn" onclick="window.print()">🖨️ 匯出 PDF / 列印</button>
                <button class="btn" onclick="toggleAllSections()">📂 展開 / 折疊全部</button>
            </div>
        </header>

        <!-- 工具列：關鍵字搜尋與分類快篩 -->
        <div class="toolbar">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" class="search-input" placeholder="即時搜尋關鍵字、標題或主題..." oninput="filterNews()">
            </div>
            <div class="filter-tabs">
                {filter_tabs_html}
            </div>
        </div>

        <!-- 數據統計看板 -->
        <div class="stats-bar">
            {stats_bar_html}
        </div>

        <!-- AI 自動摘要區 -->
        <div class="ai-summary-container">
            <div class="ai-summary-header">
                <span class="ai-badge">AI 智能綜整</span>
                <h2 class="ai-summary-title">今日全方位情報脈動</h2>
            </div>
            
            <div class="punchline-card">
                💡 今日一句總結：{punchline}
            </div>

            <div class="ai-summary-grid">
                <div class="summary-card">
                    <div class="summary-card-title" style="color: var(--accent-cyan);">🔥 今日三大重點</div>
                    <ul class="top-three-list">
                        {top_three_html}
                    </ul>
                </div>
                <div class="summary-card">
                    <div class="summary-card-title" style="color: var(--accent-green);">📈 今日投資觀察</div>
                    <p>{inv_obs}</p>
                </div>
                <div class="summary-card">
                    <div class="summary-card-title" style="color: var(--accent-purple);">💻 今日產業與科技觀察</div>
                    <p>{ind_obs} {ai_obs}</p>
                </div>
            </div>
        </div>

        <!-- TOP 10 重要新聞 (若有) -->
        <div class="top10-section" id="top10Section">
            <div class="top10-header">
                🏆 今日必讀 TOP 重點
            </div>
            <div class="top10-grid">
                {top10_html}
            </div>
        </div>

        <!-- 各分類詳細清單 -->
        <div id="allSections">
            {sections_html}
        </div>

    </div>

    <!-- 互動功能腳本 -->
    <script>
        function toggleSection(sectionId) {{
            const body = document.getElementById('body-' + sectionId);
            const arrow = document.getElementById('arrow-' + sectionId);
            if (body.classList.contains('collapsed')) {{
                body.classList.remove('collapsed');
                arrow.classList.remove('collapsed');
            }} else {{
                body.classList.add('collapsed');
                arrow.classList.add('collapsed');
            }}
        }}

        function toggleAllSections() {{
            const bodies = document.querySelectorAll('.section-body');
            const arrows = document.querySelectorAll('.toggle-arrow');
            
            let allCollapsed = true;
            for (let i = 0; i < bodies.length; i++) {{
                if (!bodies[i].classList.contains('collapsed')) {{
                    allCollapsed = false;
                    break;
                }}
            }}

            if (allCollapsed) {{
                bodies.forEach(b => b.classList.remove('collapsed'));
                arrows.forEach(a => a.classList.remove('collapsed'));
            }} else {{
                bodies.forEach(b => b.classList.add('collapsed'));
                arrows.forEach(a => a.classList.add('collapsed'));
            }}
        }}

        function filterCategory(catName, btnElem) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            btnElem.classList.add('active');
            
            const sections = document.querySelectorAll('.category-section');
            const top10 = document.getElementById('top10Section');
            if (catName === 'all') {{
                sections.forEach(sec => sec.style.display = 'block');
                if (top10) top10.style.display = 'block';
            }} else {{
                sections.forEach(sec => {{
                    if (sec.getAttribute('data-category') === catName) {{
                        sec.style.display = 'block';
                    }} else {{
                        sec.style.display = 'none';
                    }}
                }});
                if (top10) top10.style.display = 'none';
            }}
            
            filterNews();
        }}
        
        function scrollToSection(code) {{
            const section = document.getElementById('section-' + code);
            if (section) {{
                section.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                const body = document.getElementById('body-' + code);
                const arrow = document.getElementById('arrow-' + code);
                if (body && body.classList.contains('collapsed')) {{
                    body.classList.remove('collapsed');
                    arrow.classList.remove('collapsed');
                }}
            }}
        }}

        function filterNews() {{
            const input = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.news-card');
            const activeBtn = document.querySelector('.tab-btn.active');
            const activeCategory = activeBtn ? (activeBtn.getAttribute('data-category') || 'all') : 'all';
            
            cards.forEach(card => {{
                const title = (card.getAttribute('data-title') || '').toLowerCase();
                const topic = (card.getAttribute('data-topic') || '').toLowerCase();
                const cat = card.getAttribute('data-category') || '';
                
                let matchesSearch = title.includes(input) || topic.includes(input);
                let matchesCategory = (activeCategory === 'all' || cat === activeCategory);
                
                if (matchesSearch && matchesCategory) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
            
            if (input.trim() !== '') {{
                document.querySelectorAll('.section-body').forEach(b => b.classList.remove('collapsed'));
                document.querySelectorAll('.toggle-arrow').forEach(a => a.classList.remove('collapsed'));
            }}
        }}
    </script>
</body>
</html>"""
    
    html_path = REPORTS_DIR / f"{target_date}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return html_path
