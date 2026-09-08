# -*- coding: utf-8 -*-
"""
Snake Daily Report - 現代科技風與專業財經終端 HTML Dashboard 產生引擎
具備華爾街/彭博情報終端風格排版、即時快篩、卡片展開閱讀、原文直連與自適應 RWD / 列印樣式。
"""

import os
import json
from datetime import datetime
from pathlib import Path
from config import REPORTS_DIR, TOPIC_CATEGORIES

def render_html_dashboard(news_items: list, ai_summary: dict, target_date: str = None) -> Path:
    """
    將新聞與 AI 摘要渲染為高質感財經科技情報 Dashboard
    """
    if not target_date:
        target_date = datetime.now().strftime("%Y%m%d")
        
    display_date = f"{target_date[:4]}年{target_date[4:6]}月{target_date[6:]}日"
    now_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 統計各類別數量
    category_counts = {cat: 0 for cat in TOPIC_CATEGORIES.keys()}
    for item in news_items:
        cat = item.get("category", "其他")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
    total_count = len(news_items)
    
    # 選出 TOP 10 重點新聞（優先取各類首選與重要權值）
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
    top_three_items = ai_summary.get("top_three", [])
    top_three_html = "".join([
        f'''<li class="key-point-item">
            <span class="key-point-num">{i+1:02d}</span>
            <div class="key-point-text">{point}</div>
        </li>''' 
        for i, point in enumerate(top_three_items)
    ])
    inv_obs = ai_summary.get("investment_observation", "")
    ind_obs = ai_summary.get("industry_observation", "")
    ai_obs = ai_summary.get("ai_observation", "")
    punchline = ai_summary.get("punchline", "科技浪潮全面步入 AI 代理人與硬體落地元年，掌握算力槓桿與資本效率者將定義新秩序。")

    # 組裝五大分類的卡片 HTML
    sections_html = ""
    for cat_name, cat_meta in TOPIC_CATEGORIES.items():
        cat_items = [x for x in news_items if x.get("category") == cat_name]
        cat_icon = cat_meta.get("icon", "📌")
        cat_color = cat_meta.get("color", "#38bdf8")
        
        cards_html = ""
        for it in cat_items:
            cards_html += f'''
            <div class="news-card" data-category="{cat_name}" data-title="{it.get('title', '')}" data-topic="{it.get('topic', '')}" data-source="{it.get('source', '')}">
                <div class="card-header">
                    <span class="topic-tag" style="background: {cat_color}18; color: {cat_color}; border-color: {cat_color}40;">
                        {it.get('topic')}
                    </span>
                    <span class="pub-time">{it.get('publish_time')}</span>
                </div>
                <h4 class="card-title">{it.get('title')}</h4>
                <div class="summary-wrapper">
                    <p class="card-summary clamped">{it.get('summary')}</p>
                    <button class="expand-btn" onclick="toggleCardExpand(this)" title="展開閱讀完整重點">展開閱讀 ▾</button>
                </div>
                <div class="card-footer">
                    <span class="source-tag" title="{it.get('source')}">🏷️ {it.get('source')}</span>
                    <a href="{it.get('url')}" target="_blank" rel="noopener noreferrer" class="link-btn">
                        開啟原文 <span class="arrow-icon">↗</span>
                    </a>
                </div>
            </div>
            '''
            
        sections_html += f'''
        <section class="category-section" id="section-{cat_meta['code']}" data-category="{cat_name}">
            <div class="section-header" onclick="toggleSection('{cat_meta['code']}')">
                <div class="section-header-left">
                    <div class="section-icon-box" style="background: {cat_color}20; color: {cat_color}; border-color: {cat_color}40;">
                        {cat_icon}
                    </div>
                    <div>
                        <h3 class="section-title">{cat_name}動態</h3>
                        <span class="section-subtitle">SECTOR INTELLIGENCE · 即時深度追蹤</span>
                    </div>
                    <span class="section-count-badge" style="background: {cat_color}18; color: {cat_color}; border-color: {cat_color}40;">
                        {len(cat_items)} 則焦點
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

    # TOP 10 重點新聞卡片 HTML
    top10_html = ""
    for idx, it in enumerate(top10_items, 1):
        cat = it.get("category", "其他")
        cat_color = TOPIC_CATEGORIES.get(cat, {}).get("color", "#38bdf8")
        top10_html += f'''
        <div class="top10-card" data-category="{cat}" data-title="{it.get('title', '')}">
            <div class="top10-rank-col">
                <div class="top10-rank" style="color: {cat_color};">#{idx:02d}</div>
                <span class="top10-badge" style="background: {cat_color}18; color: {cat_color}; border-color: {cat_color}40;">{cat}</span>
            </div>
            <div class="top10-content">
                <div class="top10-meta">
                    <span class="top10-topic">{it.get('topic')}</span>
                    <span class="time">📅 {it.get('publish_time')}</span>
                </div>
                <h4 class="top10-title">{it.get('title')}</h4>
                <div class="summary-wrapper">
                    <p class="card-summary clamped">{it.get('summary')}</p>
                    <button class="expand-btn" onclick="toggleCardExpand(this)" title="展開閱讀完整重點">展開閱讀 ▾</button>
                </div>
                <div class="top10-footer">
                    <span class="source" title="{it.get('source')}">🏷️ 來源：{it.get('source')}</span>
                    <a href="{it.get('url')}" target="_blank" rel="noopener noreferrer" class="top10-link">
                        開啟原文 <span class="arrow-icon">↗</span>
                    </a>
                </div>
            </div>
        </div>
        '''

    # 動態產生篩選標籤按鈕
    filter_tabs_html = f'<button class="tab-btn active" data-category="all" onclick="filterCategory(\'all\', this)">全部 ({total_count})</button>'
    for cat_name, cat_meta in TOPIC_CATEGORIES.items():
        filter_tabs_html += f'\n                <button class="tab-btn" data-category="{cat_name}" onclick="filterCategory(\'{cat_name}\', this)">{cat_name} ({category_counts.get(cat_name, 0)})</button>'

    # 動態產生統計看盤看板
    stats_bar_html = ""
    for cat_name, cat_meta in TOPIC_CATEGORIES.items():
        code = cat_meta["code"]
        icon = cat_meta.get("icon", "📌")
        color = cat_meta.get("color", "#38bdf8")
        stats_bar_html += f'''
            <div class="stat-card" onclick="scrollToSection('{code}')" style="--card-accent: {color};">
                <div class="stat-info">
                    <div class="stat-name">{cat_name}</div>
                    <div class="stat-num">{category_counts.get(cat_name, 0)} <span class="stat-unit">則</span></div>
                </div>
                <div class="stat-icon-wrapper" style="background: {color}15; color: {color};">
                    {icon}
                </div>
            </div>'''

    html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snake Daily Report · 全球科技與財經焦點 - {display_date}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700;800&family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-body: #080d1a;
            --bg-surface: #0e1628;
            --bg-card: rgba(16, 24, 44, 0.85);
            --bg-card-hover: rgba(24, 36, 66, 0.95);
            --bg-glass: rgba(13, 21, 38, 0.7);
            
            --border-subtle: rgba(148, 163, 184, 0.12);
            --border-focus: rgba(56, 189, 248, 0.45);
            --border-card: rgba(56, 189, 248, 0.15);
            
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            
            --accent-cyan: #38bdf8;
            --accent-blue: #3b82f6;
            --accent-indigo: #6366f1;
            --accent-purple: #a855f7;
            --accent-green: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            
            --shadow-subtle: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
            --shadow-glow: 0 0 25px -5px rgba(56, 189, 248, 0.25);
            
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
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Noto Sans TC", "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-primary);
            line-height: 1.6;
            padding-bottom: 80px;
            background-image: 
                radial-gradient(circle at 10% 0%, rgba(56, 189, 248, 0.10) 0%, transparent 40%),
                radial-gradient(circle at 90% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 45%),
                linear-gradient(to bottom, #080d1a, #0b1122 60%, #080d1a);
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
        }}

        .container {{
            max-width: 1320px;
            margin: 0 auto;
            padding: 30px 24px;
        }}

        /* --- 頂部金融終端 Header --- */
        .terminal-header {{
            background: linear-gradient(135deg, rgba(17, 24, 39, 0.95), rgba(15, 23, 42, 0.9));
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-card);
            border-radius: var(--radius-lg);
            padding: 26px 32px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
            box-shadow: var(--shadow-subtle);
            position: relative;
            overflow: hidden;
        }}
        .terminal-header::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-indigo), var(--accent-purple), var(--accent-green));
        }}

        .brand-pill {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(56, 189, 248, 0.1);
            color: var(--accent-cyan);
            border: 1px solid rgba(56, 189, 248, 0.3);
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: 20px;
            margin-bottom: 8px;
        }}
        .live-dot {{
            width: 7px;
            height: 7px;
            background-color: var(--accent-green);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--accent-green);
            animation: pulse-glow 2s infinite ease-in-out;
        }}
        @keyframes pulse-glow {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.4; transform: scale(0.85); }}
        }}

        .header-title {{
            font-size: 30px;
            font-weight: 900;
            letter-spacing: -0.5px;
            background: linear-gradient(to right, #ffffff, #e2e8f0 60%, var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }}
        .header-subtitle {{
            color: var(--text-muted);
            font-size: 13px;
            letter-spacing: 0.5px;
        }}
        .header-meta-bar {{
            display: flex;
            align-items: center;
            gap: 18px;
            flex-wrap: wrap;
            font-size: 13px;
            color: var(--text-secondary);
            margin-top: 10px;
            font-family: 'JetBrains Mono', monospace;
        }}
        .header-meta-item {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .header-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .btn {{
            padding: 9px 18px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-card);
            background: rgba(22, 32, 54, 0.7);
            color: var(--text-primary);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            user-select: none;
        }}
        .btn:hover {{
            background: rgba(56, 189, 248, 0.18);
            border-color: var(--accent-cyan);
            color: #ffffff;
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.3);
            transform: translateY(-1px);
        }}
        .btn-primary {{
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(99, 102, 241, 0.25));
            border-color: var(--accent-cyan);
            color: #ffffff;
        }}

        /* --- 盤面看盤數據儀表板 (Stats Bar) --- */
        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 14px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-subtle);
            border-left: 3px solid var(--card-accent, var(--accent-cyan));
            border-radius: var(--radius-md);
            padding: 16px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
            border-color: var(--card-accent, var(--accent-cyan));
            background: var(--bg-card-hover);
            box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.4);
        }}
        .stat-info .stat-name {{
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 4px;
        }}
        .stat-info .stat-num {{
            font-size: 24px;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            color: #ffffff;
            line-height: 1.1;
        }}
        .stat-unit {{
            font-size: 13px;
            font-weight: 500;
            color: var(--text-dim);
            margin-left: 2px;
        }}
        .stat-icon-wrapper {{
            font-size: 22px;
            width: 44px;
            height: 44px;
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}

        /* --- 快捷工具列 (搜尋與篩選) --- */
        .toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 28px;
            padding: 14px 20px;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-subtle);
        }}
        .search-box {{
            flex: 1;
            min-width: 280px;
            position: relative;
        }}
        .search-input {{
            width: 100%;
            padding: 10px 16px 10px 42px;
            background: rgba(10, 15, 28, 0.85);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-sm);
            color: var(--text-primary);
            font-size: 14px;
            outline: none;
            transition: all 0.2s ease;
        }}
        .search-input:focus {{
            border-color: var(--accent-cyan);
            background: rgba(13, 21, 38, 0.95);
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.25);
        }}
        .search-icon {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-dim);
            font-size: 15px;
        }}
        .filter-tabs {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .tab-btn {{
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 12.5px;
            font-weight: 600;
            border: 1px solid var(--border-subtle);
            background: rgba(18, 27, 48, 0.5);
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.2s ease;
            user-select: none;
        }}
        .tab-btn.active, .tab-btn:hover {{
            background: rgba(56, 189, 248, 0.16);
            color: var(--accent-cyan);
            border-color: var(--accent-cyan);
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.2);
        }}

        /* --- 彭博/高盛風格 AI 總經與戰略洞察晨會區塊 --- */
        .executive-summary-container {{
            background: linear-gradient(135deg, rgba(16, 25, 46, 0.92), rgba(11, 18, 34, 0.98));
            border: 1px solid rgba(99, 102, 241, 0.25);
            border-radius: var(--radius-lg);
            padding: 28px;
            margin-bottom: 34px;
            box-shadow: var(--shadow-subtle);
            position: relative;
        }}
        .summary-header-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 16px;
            margin-bottom: 22px;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .summary-header-title-group {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .brief-badge {{
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
            color: #050811;
            font-size: 11.5px;
            font-weight: 800;
            letter-spacing: 0.5px;
            padding: 4px 12px;
            border-radius: 12px;
            text-transform: uppercase;
        }}
        .summary-main-title {{
            font-size: 21px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.3px;
        }}
        .summary-date-tag {{
            font-size: 12px;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
        }}

        /* 今日一句核心 Takeaway 卡片 */
        .punchline-banner {{
            background: linear-gradient(90deg, rgba(56, 189, 248, 0.12), rgba(99, 102, 241, 0.06));
            border-left: 4px solid var(--accent-cyan);
            border-radius: 0 var(--radius-md) var(--radius-md) 0;
            padding: 16px 22px;
            margin-bottom: 24px;
            display: flex;
            align-items: flex-start;
            gap: 12px;
            box-shadow: inset 0 0 15px rgba(56, 189, 248, 0.05);
        }}
        .punchline-icon {{
            font-size: 20px;
            color: var(--accent-amber);
            flex-shrink: 0;
            margin-top: 1px;
        }}
        .punchline-content {{
            font-size: 15px;
            font-weight: 600;
            color: #f1f5f9;
            line-height: 1.6;
        }}
        .punchline-label {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-cyan);
            font-weight: 800;
            margin-bottom: 2px;
        }}

        /* 三欄式分析卡片 Grid */
        .strategic-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
        }}
        .strategic-card {{
            background: rgba(10, 16, 30, 0.65);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            position: relative;
        }}
        .strategic-card-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }}
        .strategic-card p {{
            font-size: 13.5px;
            color: var(--text-secondary);
            line-height: 1.7;
            text-align: justify;
        }}

        /* 三大亮點清單 */
        .key-points-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .key-point-item {{
            display: flex;
            gap: 12px;
            align-items: flex-start;
        }}
        .key-point-num {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent-cyan);
            font-family: 'JetBrains Mono', monospace;
            font-weight: 800;
            font-size: 11px;
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 6px;
            padding: 2px 6px;
            margin-top: 3px;
            flex-shrink: 0;
        }}
        .key-point-text {{
            font-size: 13.5px;
            color: var(--text-secondary);
            line-height: 1.6;
        }}

        /* --- 今日必讀 TOP 焦點新聞 (Top 10 Section) --- */
        .top10-section {{
            margin-bottom: 38px;
        }}
        .section-headline {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
            border-left: 4px solid var(--accent-cyan);
            padding-left: 14px;
        }}
        .section-headline-title {{
            font-size: 20px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.2px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section-headline-meta {{
            font-size: 12px;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
        }}

        .top10-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 18px;
        }}
        .top10-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 18px;
            display: flex;
            gap: 16px;
            transition: all 0.25s ease;
            position: relative;
        }}
        .top10-card:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-focus);
            transform: translateY(-2px);
            box-shadow: 0 10px 28px -6px rgba(0, 0, 0, 0.5);
        }}
        .top10-rank-col {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            flex-shrink: 0;
        }}
        .top10-rank {{
            font-size: 24px;
            font-weight: 900;
            font-family: 'JetBrains Mono', monospace;
            line-height: 1;
        }}
        .top10-badge {{
            font-size: 10px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 10px;
            border: 1px solid;
            white-space: nowrap;
        }}
        .top10-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        .top10-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 6px;
        }}
        .top10-topic {{
            color: var(--accent-cyan);
            font-weight: 600;
        }}
        .top10-title {{
            font-size: 15px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 8px;
            line-height: 1.45;
            letter-spacing: -0.2px;
        }}
        .top10-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 12px;
            color: var(--text-muted);
        }}
        .top10-link {{
            color: var(--accent-cyan);
            text-decoration: none;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.2s;
        }}
        .top10-link:hover {{
            color: #ffffff;
            text-decoration: underline;
        }}

        /* --- 摘要展開/收合核心樣式 --- */
        .summary-wrapper {{
            margin-bottom: 12px;
            flex-grow: 1;
        }}
        .card-summary {{
            font-size: 13.5px;
            color: var(--text-secondary);
            line-height: 1.65;
            transition: all 0.3s ease;
            word-break: break-word;
        }}
        /* 預設折疊狀態：3 行省略截斷 */
        .card-summary.clamped {{
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        /* 展開按鈕樣式 */
        .expand-btn {{
            background: transparent;
            border: none;
            color: var(--accent-cyan);
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            padding: 4px 0 0 0;
            margin-top: 4px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: color 0.2s;
            outline: none;
        }}
        .expand-btn:hover {{
            color: #ffffff;
            text-decoration: underline;
        }}

        /* --- 各大產業分類折疊區塊 (Category Section) --- */
        .category-section {{
            margin-bottom: 26px;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            overflow: hidden;
            transition: border-color 0.25s ease;
            box-shadow: var(--shadow-subtle);
        }}
        .category-section:hover {{
            border-color: rgba(56, 189, 248, 0.25);
        }}
        .section-header {{
            padding: 18px 24px;
            background: rgba(13, 20, 36, 0.7);
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
            transition: background 0.2s ease;
        }}
        .section-header:hover {{
            background: rgba(22, 33, 58, 0.85);
        }}
        .section-header-left {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .section-icon-box {{
            width: 40px;
            height: 40px;
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            border: 1px solid;
            flex-shrink: 0;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.2px;
        }}
        .section-subtitle {{
            display: block;
            font-size: 11px;
            font-weight: 600;
            color: var(--text-dim);
            letter-spacing: 0.8px;
            margin-top: 1px;
        }}
        .section-count-badge {{
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            border: 1px solid;
            font-family: 'JetBrains Mono', monospace;
        }}
        .toggle-arrow {{
            color: var(--text-muted);
            font-size: 13px;
            transition: transform 0.3s ease;
        }}
        .toggle-arrow.collapsed {{
            transform: rotate(-90deg);
        }}
        .section-body {{
            padding: 22px;
            display: block;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .section-body.collapsed {{
            display: none;
        }}

        /* --- 新聞卡片 Grid --- */
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
            gap: 18px;
        }}
        .news-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 18px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .news-card:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-focus);
            transform: translateY(-2px);
            box-shadow: 0 12px 28px -6px rgba(0, 0, 0, 0.45);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .topic-tag {{
            font-size: 11.5px;
            font-weight: 700;
            padding: 2px 9px;
            border-radius: var(--radius-sm);
            border: 1px solid;
        }}
        .pub-time {{
            font-size: 11.5px;
            color: var(--text-dim);
            font-family: 'JetBrains Mono', monospace;
        }}
        .card-title {{
            font-size: 15.5px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 10px;
            line-height: 1.45;
            letter-spacing: -0.2px;
        }}
        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding-top: 12px;
            margin-top: 4px;
            font-size: 12px;
        }}
        .source-tag {{
            color: var(--text-muted);
            max-width: 170px;
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
            transition: all 0.2s ease;
            background: rgba(56, 189, 248, 0.08);
            padding: 4px 10px;
            border-radius: var(--radius-sm);
            border: 1px solid rgba(56, 189, 248, 0.2);
        }}
        .link-btn:hover {{
            color: #ffffff;
            background: var(--accent-cyan);
            color: #080d1a;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
        }}
        .arrow-icon {{
            font-weight: 700;
            transition: transform 0.2s;
        }}
        .link-btn:hover .arrow-icon {{
            transform: translate(2px, -2px);
        }}

        /* --- 列印與 PDF 匯出最佳化樣式 --- */
        @media print {{
            body {{
                background: #ffffff !important;
                color: #0f172a !important;
                background-image: none !important;
            }}
            .terminal-header, .executive-summary-container, .top10-card, .category-section, .news-card {{
                background: #ffffff !important;
                border: 1px solid #cbd5e1 !important;
                box-shadow: none !important;
                color: #0f172a !important;
                break-inside: avoid;
            }}
            .header-title, .summary-main-title, .card-title, .top10-title {{
                -webkit-text-fill-color: #0f172a !important;
                color: #0f172a !important;
            }}
            .toolbar, .header-actions, .toggle-arrow, .expand-btn {{
                display: none !important;
            }}
            .card-summary.clamped {{
                display: block !important;
            }}
            .card-summary, p {{
                color: #334155 !important;
            }}
            .section-body {{
                display: block !important;
            }}
        }}

        /* --- RWD 行動裝置優化 --- */
        @media (max-width: 768px) {{
            .terminal-header {{
                flex-direction: column;
                align-items: flex-start;
                padding: 20px;
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
            .strategic-grid {{
                grid-template-columns: 1fr;
            }}
            .top10-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 頂部金融終端 Header -->
        <header class="terminal-header">
            <div class="header-title-area">
                <div class="brand-pill">
                    <span class="live-dot"></span>
                    SNAKE INTELLIGENCE · 財經與科技情報監測
                </div>
                <h1 class="header-title">Snake Daily Report</h1>
                <p class="header-subtitle">GLOBAL TECH & CAPITAL MARKETS TERMINAL · 全球科技與資本市場日報</p>
                <div class="header-meta-bar">
                    <span class="header-meta-item">📅 {display_date}</span>
                    <span class="header-meta-item">🕒 監測產出時間：{now_time_str}</span>
                    <span class="header-meta-item">📊 深度收錄：共 {total_count} 則重點情報</span>
                </div>
            </div>
            <div class="header-actions">
                <button class="btn btn-primary" onclick="toggleAllSummaries()">📖 展開 / 收合全部摘要</button>
                <button class="btn" onclick="toggleAllSections()">📂 展開 / 折疊全部分類</button>
                <button class="btn" onclick="window.print()">🖨️ 匯出 PDF / 列印</button>
            </div>
        </header>

        <!-- 數據統計看盤看板 -->
        <div class="stats-bar">
            {stats_bar_html}
        </div>

        <!-- 工具列：關鍵字搜尋與分類快篩 -->
        <div class="toolbar">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" class="search-input" placeholder="即時檢索關鍵字、公司、主題或股票代號（例如：台積電、NVIDIA、聯準會、AI Agent）..." oninput="filterNews()">
            </div>
            <div class="filter-tabs">
                {filter_tabs_html}
            </div>
        </div>

        <!-- 彭博/高盛風格 AI 總經與產業深度綜整 -->
        <div class="executive-summary-container">
            <div class="summary-header-row">
                <div class="summary-header-title-group">
                    <span class="brief-badge">EXECUTIVE BRIEF</span>
                    <h2 class="summary-main-title">今日全方位情報與資本市場脈動</h2>
                </div>
                <span class="summary-date-tag">INTELLIGENCE DATE: {display_date}</span>
            </div>
            
            <div class="punchline-banner">
                <span class="punchline-icon">💡</span>
                <div>
                    <div class="punchline-label">EXECUTIVE TAKEAWAY · 今日一句核心綜述</div>
                    <div class="punchline-content">{punchline}</div>
                </div>
            </div>

            <div class="strategic-grid">
                <div class="strategic-card">
                    <div class="strategic-card-title" style="color: var(--accent-cyan);">🔥 今日三大重磅焦點</div>
                    <ul class="key-points-list">
                        {top_three_html}
                    </ul>
                </div>
                <div class="strategic-card">
                    <div class="strategic-card-title" style="color: var(--accent-green);">📈 資本市場與資金脈動</div>
                    <p>{inv_obs}</p>
                </div>
                <div class="strategic-card">
                    <div class="strategic-card-title" style="color: var(--accent-purple);">💻 產業戰略與科技前沿</div>
                    <p>{ind_obs} {ai_obs}</p>
                </div>
            </div>
        </div>

        <!-- 今日必讀 TOP 10 焦點 -->
        <div class="top10-section" id="top10Section">
            <div class="section-headline">
                <h3 class="section-headline-title">
                    🏆 今日必讀 TOP 重點
                </h3>
                <span class="section-headline-meta">HEAVYWEIGHT HEADLINES</span>
            </div>
            <div class="top10-grid">
                {top10_html}
            </div>
        </div>

        <!-- 各板塊深度情報清單 -->
        <div id="allSections">
            {sections_html}
        </div>

    </div>

    <!-- 前端互動與展開功能腳本 -->
    <script>
        // 單卡片摘要展開 / 收合
        function toggleCardExpand(btn) {{
            const wrapper = btn.closest('.summary-wrapper');
            if (!wrapper) return;
            const summary = wrapper.querySelector('.card-summary');
            if (!summary) return;
            
            if (summary.classList.contains('clamped')) {{
                summary.classList.remove('clamped');
                btn.innerText = '收合內容 ▴';
            }} else {{
                summary.classList.add('clamped');
                btn.innerText = '展開閱讀 ▾';
            }}
        }}

        // 全局摘要一鍵全展開 / 全收合
        let allSummariesExpanded = false;
        function toggleAllSummaries() {{
            allSummariesExpanded = !allSummariesExpanded;
            const summaries = document.querySelectorAll('.card-summary');
            const btns = document.querySelectorAll('.expand-btn');
            
            summaries.forEach(s => {{
                if (allSummariesExpanded) {{
                    s.classList.remove('clamped');
                }} else {{
                    s.classList.add('clamped');
                }}
            }});
            
            btns.forEach(b => {{
                b.innerText = allSummariesExpanded ? '收合內容 ▴' : '展開閱讀 ▾';
            }});
        }}

        // 單分類折疊 / 展開
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

        // 全部分類展開 / 折疊
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

        // 分類標籤快速切換
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
        
        // 點擊看盤卡片平滑滾動至對應分類
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

        // 即時關鍵字搜尋過濾
        function filterNews() {{
            const input = document.getElementById('searchInput').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.news-card');
            const activeBtn = document.querySelector('.tab-btn.active');
            const activeCategory = activeBtn ? (activeBtn.getAttribute('data-category') || 'all') : 'all';
            
            cards.forEach(card => {{
                const title = (card.getAttribute('data-title') || '').toLowerCase();
                const topic = (card.getAttribute('data-topic') || '').toLowerCase();
                const source = (card.getAttribute('data-source') || '').toLowerCase();
                const summaryElem = card.querySelector('.card-summary');
                const summaryText = summaryElem ? summaryElem.innerText.toLowerCase() : '';
                const cat = card.getAttribute('data-category') || '';
                
                let matchesSearch = !input || title.includes(input) || topic.includes(input) || source.includes(input) || summaryText.includes(input);
                let matchesCategory = (activeCategory === 'all' || cat === activeCategory);
                
                if (matchesSearch && matchesCategory) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
            
            if (input !== '') {{
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
