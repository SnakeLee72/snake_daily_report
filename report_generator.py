# -*- coding: utf-8 -*-
"""
Snake Daily Report - 現代金融與科技情報終端 HTML Dashboard 產生引擎
融合 Bloomberg Intelligence / Financial Times 現代專業排版：
1. 頂部終端導航、深淺主題切換、即時檢索
2. 今日一句話 (Executive Takeaway)
3. 市場溫度與多空風向儀表板 (Market Sentiment)
4. 今日必看 3 件事 (The Big 3 雜誌頭條排版)
5. 產業影響鏈矩陣 (Supply Chain Impact Matrix)
6. 五大板塊「一句話結論」與深度卡片庫 (含平滑展開/原文直連)
7. 今日市場雜訊與速讀 (Market Noise)
8. 明日關鍵觀察清單 (Tomorrow's Catalyst Watchlist)
9. 資料來源與金融合規免責聲明 (Compliance & Disclaimer)
10. 手機專屬底部浮動導航列 (Mobile Bottom Nav Bar)
"""

import os
import json
from datetime import datetime
from pathlib import Path
from config import REPORTS_DIR, TOPIC_CATEGORIES

def render_html_dashboard(news_items: list, ai_summary: dict, target_date: str = None) -> Path:
    """
    將新聞與決策級 AI 摘要渲染為高質感金融情報終端 Dashboard
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
    
    # 今日一句話
    punchline = ai_summary.get(
        "punchline", 
        "全球科技浪潮全面步入 AI 代理人商業落地與硬體供應鏈深水區，掌握算力槓桿與資本效率者將定義新秩序。"
    )
    
    # 1. 市場溫度儀表板 (Market Sentiment)
    sentiment_data = ai_summary.get("market_sentiment", {})
    sentiment_html = ""
    default_indicators = [
        ("tech_momentum", "🚀 全球科技動能", "強勁擴張", "AI 代理人與基礎設施投資持續加速", "var(--accent-cyan)", "up"),
        ("capital_flow", "⚖️ 宏觀資本流向", "震盪輪動", "資金高度聚焦科技權值股與避險資產", "var(--accent-amber)", "neutral"),
        ("supply_chain", "🏭 硬體供應鏈景氣", "高檔滿載", "AI 伺服器拉貨強勁帶動規格全面升級", "var(--accent-green)", "up"),
        ("risk_level", "🛡️ 總體市場風險", "中等觀望", "美債殖利率維持高位，靜待通膨數據指引", "var(--accent-purple)", "warning")
    ]
    for key, def_title, def_status, def_desc, def_color, def_trend in default_indicators:
        val = sentiment_data.get(key, {})
        title = val.get("title", def_title)
        status = val.get("status", def_status)
        desc = val.get("desc", def_desc)
        badge_color = val.get("badge_color", def_color)
        trend = val.get("trend", def_trend)
        trend_icon = "▲" if trend == "up" else ("▼" if trend == "down" else "◆")
        
        sentiment_html += f'''
        <div class="sentiment-card" style="--indicator-color: {badge_color};">
            <div class="sentiment-card-top">
                <span class="sentiment-title">{title}</span>
                <span class="sentiment-badge" style="background: {badge_color}18; color: {badge_color}; border-color: {badge_color}44;">
                    {trend_icon} {status}
                </span>
            </div>
            <div class="sentiment-desc">{desc}</div>
        </div>
        '''

    # 2. 今日必看 3 件事 (The Big 3 雜誌頭條排版)
    big_three_items = ai_summary.get("the_big_three", [])
    if not big_three_items and len(news_items) >= 3:
        for i, it in enumerate(news_items[:3], 1):
            big_three_items.append({
                "rank": i,
                "category": it.get("category", "焦點"),
                "topic": it.get("topic", ""),
                "headline": it.get("title", ""),
                "why_it_matters": it.get("summary", ""),
                "key_metric": "產業重大進展",
                "url": it.get("url", "#")
            })

    big_three_html = ""
    for item in big_three_items:
        r = item.get("rank", 1)
        cat = item.get("category", "核心焦點")
        top = item.get("topic", "")
        hl = item.get("headline", "")
        why = item.get("why_it_matters", "")
        metric = item.get("key_metric", "")
        url = item.get("url", "#")
        cat_color = TOPIC_CATEGORIES.get(cat, {}).get("color", "var(--accent-cyan)")
        
        is_hero = (r == 1)
        card_class = "big-three-card hero-lead" if is_hero else "big-three-card"
        
        big_three_html += f'''
        <div class="{card_class}">
            <div class="big-three-header">
                <div class="big-three-rank" style="color: {cat_color};">#{r:02d}</div>
                <div class="big-three-tags">
                    <span class="badge-cat" style="background: {cat_color}18; color: {cat_color}; border-color: {cat_color}40;">{cat}</span>
                    {f'<span class="badge-topic">{top}</span>' if top else ''}
                </div>
                {f'<span class="hero-label">★ TOP STORY OF THE DAY</span>' if is_hero else ''}
            </div>
            <h3 class="big-three-headline">{hl}</h3>
            
            <div class="why-it-matters-box">
                <div class="box-label">💡 為什麼重要 (WHY IT MATTERS)</div>
                <p class="box-content">{why}</p>
            </div>
            
            <div class="big-three-footer">
                <div class="metric-pill">
                    <span class="metric-icon">📊</span>
                    <span class="metric-text">{metric}</span>
                </div>
                <a href="{url}" target="_blank" rel="noopener noreferrer" class="link-btn-hero">
                    開啟原文直連 <span class="arrow-icon">↗</span>
                </a>
            </div>
        </div>
        '''

    # 3. 產業影響鏈 (Supply Chain Impact Matrix)
    impact_items = ai_summary.get("impact_chain", [])
    impact_html = ""
    for imp in impact_items:
        impact_html += f'''
        <div class="impact-chain-card">
            <div class="impact-node trigger-node">
                <div class="node-badge">⚡ 驅動事件 (TRIGGER)</div>
                <div class="node-title">{imp.get('trigger')}</div>
            </div>
            <div class="impact-arrow">➔</div>
            <div class="impact-node process-node">
                <div class="node-badge">⚙️ 規格/零組件影響 (IMPACT)</div>
                <div class="node-title">{imp.get('impacted_area')}</div>
            </div>
            <div class="impact-arrow">➔</div>
            <div class="impact-node target-node">
                <div class="node-badge">🎯 台美關鍵受惠標的 (BENEFICIARIES)</div>
                <div class="node-title highlighted-stocks">{imp.get('key_beneficiaries')}</div>
            </div>
        </div>
        '''

    # 4. 各大板塊組裝 (含板塊一句話結論 Sector Bottom Lines)
    sector_bottom_lines = ai_summary.get("sector_bottom_lines", {})
    sections_html = ""
    for cat_name, cat_meta in TOPIC_CATEGORIES.items():
        cat_items = [x for x in news_items if x.get("category") == cat_name]
        cat_icon = cat_meta.get("icon", "📌")
        cat_color = cat_meta.get("color", "#38bdf8")
        cat_line = sector_bottom_lines.get(
            cat_name, 
            f"今日 {cat_name} 板塊整體聚焦產業前線動能，指標企業持續推進關鍵戰略布局。"
        )
        
        cards_html = ""
        for it in cat_items:
            cards_html += f'''
            <div class="news-card" data-category="{cat_name}" data-title="{it.get('title', '')}" data-topic="{it.get('topic', '')}" data-source="{it.get('source', '')}">
                <div class="card-header">
                    <span class="topic-tag" style="background: {cat_color}16; color: {cat_color}; border-color: {cat_color}40;">
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
                    <div class="section-icon-box" style="background: {cat_color}18; color: {cat_color}; border-color: {cat_color}40;">
                        {cat_icon}
                    </div>
                    <div>
                        <h3 class="section-title">{cat_name}動態</h3>
                        <span class="section-subtitle">SECTOR INTELLIGENCE · 深度即時追蹤</span>
                    </div>
                    <span class="section-count-badge" style="background: {cat_color}16; color: {cat_color}; border-color: {cat_color}40;">
                        {len(cat_items)} 則焦點
                    </span>
                </div>
                <div class="section-header-right">
                    <span class="toggle-arrow" id="arrow-{cat_meta['code']}">▼</span>
                </div>
            </div>
            <div class="section-bottom-line-bar">
                <span class="bottom-line-tag" style="color: {cat_color};">📌 一句話結論</span>
                <span class="bottom-line-text">{cat_line}</span>
            </div>
            <div class="section-body" id="body-{cat_meta['code']}">
                <div class="news-grid">
                    {cards_html}
                </div>
            </div>
        </section>
        '''

    # 5. 今日雜訊與速報清單 (Market Noise & Quick Hits)
    market_noise_items = ai_summary.get("market_noise", [])
    noise_html = ""
    if market_noise_items:
        for n in market_noise_items:
            noise_html += f'''
            <div class="noise-item">
                <span class="noise-cat">[{n.get('category', '速讀')}]</span>
                <a href="{n.get('url', '#')}" target="_blank" class="noise-title">{n.get('title')}</a>
                <span class="noise-source">({n.get('source', '')})</span>
            </div>
            '''

    # 6. 明日觀察清單 (Tomorrow's Catalyst Watchlist)
    watchlist_items = ai_summary.get("tomorrow_watchlist", [])
    watchlist_html = ""
    for idx, w in enumerate(watchlist_items, 1):
        watchlist_html += f'''
        <li class="watchlist-item">
            <span class="watchlist-bullet">0{idx}</span>
            <span class="watchlist-text">{w}</span>
        </li>
        '''

    # 7. 篩選標籤按鈕
    filter_tabs_html = f'<button class="tab-btn active" data-category="all" onclick="filterCategory(\'all\', this)">全部 ({total_count})</button>'
    for cat_name, cat_meta in TOPIC_CATEGORIES.items():
        filter_tabs_html += f'\n                <button class="tab-btn" data-category="{cat_name}" onclick="filterCategory(\'{cat_name}\', this)">{cat_name} ({category_counts.get(cat_name, 0)})</button>'

    # 8. 統計看盤儀表板 (Stats Bar)
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
<html lang="zh-TW" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snake Daily Report · 全球科技與財經決策日報 - {display_date}</title>
    <meta name="description" content="每日全球科技、AI、半導體、Notebook/ODM、台股美股與宏觀市場決策情報">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700;800&family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            /* 預設深色主題（彭博深曜藍黑調） */
            --bg-body: #070b14;
            --bg-surface: #0e1526;
            --bg-surface-elevated: #131c33;
            --bg-card: rgba(16, 24, 44, 0.85);
            --bg-card-hover: rgba(24, 36, 66, 0.95);
            --bg-lead-hero: linear-gradient(135deg, rgba(16, 32, 60, 0.9), rgba(12, 20, 38, 0.95));
            
            --border-subtle: rgba(148, 163, 184, 0.12);
            --border-focus: rgba(56, 189, 248, 0.45);
            --border-card: rgba(56, 189, 248, 0.16);
            
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

        /* 淺色主題支援（金融時報風格清爽紙質感） */
        [data-theme="light"] {{
            --bg-body: #f8fafc;
            --bg-surface: #ffffff;
            --bg-surface-elevated: #f1f5f9;
            --bg-card: #ffffff;
            --bg-card-hover: #f8fafc;
            --bg-lead-hero: linear-gradient(135deg, #f0f9ff, #e0f2fe);
            
            --border-subtle: rgba(148, 163, 184, 0.3);
            --border-focus: rgba(2, 132, 199, 0.6);
            --border-card: rgba(2, 132, 199, 0.2);
            
            --text-primary: #0f172a;
            --text-secondary: #334155;
            --text-muted: #64748b;
            --text-dim: #94a3b8;
            
            --accent-cyan: #0284c7;
            --accent-blue: #2563eb;
            --accent-indigo: #4f46e5;
            --accent-purple: #9333ea;
            --accent-green: #059669;
            --accent-amber: #d97706;
            --accent-rose: #e11d48;
            
            --shadow-subtle: 0 4px 16px -2px rgba(0, 0, 0, 0.08);
            --shadow-glow: 0 0 20px -5px rgba(2, 132, 199, 0.2);
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
            padding-bottom: 90px;
            background-image: 
                radial-gradient(circle at 10% 0%, rgba(56, 189, 248, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 90% 20%, rgba(99, 102, 241, 0.06) 0%, transparent 45%);
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
            transition: background-color 0.3s ease, color 0.3s ease;
        }}

        .container {{
            max-width: 1320px;
            margin: 0 auto;
            padding: 24px 20px;
        }}

        /* --- 頂部金融終端 Header --- */
        .terminal-header {{
            background: var(--bg-surface);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-card);
            border-radius: var(--radius-lg);
            padding: 24px 30px;
            margin-bottom: 22px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 18px;
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
            background: rgba(56, 189, 248, 0.12);
            color: var(--accent-cyan);
            border: 1px solid rgba(56, 189, 248, 0.3);
            font-size: 11px;
            font-weight: 800;
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
            50% {{ opacity: 0.3; transform: scale(0.85); }}
        }}

        .header-title {{
            font-size: 28px;
            font-weight: 900;
            letter-spacing: -0.5px;
            margin-bottom: 4px;
        }}
        .header-subtitle {{
            color: var(--text-muted);
            font-size: 13px;
            letter-spacing: 0.4px;
        }}
        .header-meta-bar {{
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
            font-size: 12.5px;
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
            gap: 10px;
            flex-wrap: wrap;
        }}
        .btn {{
            padding: 8px 16px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-card);
            background: var(--bg-surface-elevated);
            color: var(--text-primary);
            font-size: 12.5px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            user-select: none;
        }}
        .btn:hover {{
            border-color: var(--accent-cyan);
            color: var(--accent-cyan);
            transform: translateY(-1px);
        }}
        .btn-primary {{
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(99, 102, 241, 0.25));
            border-color: var(--accent-cyan);
            color: var(--text-primary);
        }}

        /* --- 模組 2: 今日一句話 (Executive Takeaway) --- */
        .takeaway-banner {{
            background: linear-gradient(90deg, rgba(56, 189, 248, 0.12), rgba(99, 102, 241, 0.08));
            border-left: 5px solid var(--accent-cyan);
            border-radius: 0 var(--radius-md) var(--radius-md) 0;
            padding: 18px 24px;
            margin-bottom: 22px;
            display: flex;
            align-items: flex-start;
            gap: 14px;
            box-shadow: var(--shadow-subtle);
        }}
        .takeaway-icon {{
            font-size: 24px;
            color: var(--accent-amber);
            flex-shrink: 0;
            margin-top: 2px;
        }}
        .takeaway-label {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: var(--accent-cyan);
            font-weight: 800;
            margin-bottom: 3px;
        }}
        .takeaway-text {{
            font-size: 16px;
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1.55;
        }}

        /* --- 模組 3: 市場溫度與多空風向儀表板 (Market Sentiment) --- */
        .sentiment-section {{
            margin-bottom: 24px;
        }}
        .section-tag-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
        }}
        .section-tag-title {{
            font-size: 13px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .sentiment-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 14px;
        }}
        .sentiment-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-top: 3px solid var(--indicator-color);
            border-radius: var(--radius-md);
            padding: 16px 18px;
            box-shadow: var(--shadow-subtle);
            transition: all 0.25s ease;
        }}
        .sentiment-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.3);
        }}
        .sentiment-card-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .sentiment-title {{
            font-size: 13px;
            font-weight: 700;
            color: var(--text-primary);
        }}
        .sentiment-badge {{
            font-size: 11.5px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 6px;
            border: 1px solid;
            font-family: 'JetBrains Mono', monospace;
        }}
        .sentiment-desc {{
            font-size: 12.5px;
            color: var(--text-secondary);
            line-height: 1.5;
        }}

        /* --- 模組 4: 今日必看 3 件事 (The Big 3 特刊頭條) --- */
        .big-three-section {{
            margin-bottom: 30px;
        }}
        .big-three-grid {{
            display: grid;
            grid-template-columns: 1.35fr 1fr 1fr;
            gap: 18px;
        }}
        .big-three-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 22px;
            display: flex;
            flex-direction: column;
            box-shadow: var(--shadow-subtle);
            transition: all 0.25s ease;
            position: relative;
        }}
        .big-three-card:hover {{
            transform: translateY(-2px);
            border-color: var(--border-focus);
            box-shadow: 0 12px 30px -6px rgba(0, 0, 0, 0.45);
        }}
        .big-three-card.hero-lead {{
            background: var(--bg-lead-hero);
            border-color: rgba(56, 189, 248, 0.35);
        }}
        .hero-label {{
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.8px;
            color: var(--accent-amber);
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid rgba(245, 158, 11, 0.3);
            padding: 2px 8px;
            border-radius: 10px;
            margin-left: auto;
        }}
        .big-three-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }}
        .big-three-rank {{
            font-size: 26px;
            font-weight: 900;
            font-family: 'JetBrains Mono', monospace;
            line-height: 1;
        }}
        .big-three-tags {{
            display: flex;
            gap: 6px;
            align-items: center;
        }}
        .badge-cat {{
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 12px;
            border: 1px solid;
        }}
        .badge-topic {{
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
        }}
        .big-three-headline {{
            font-size: 17px;
            font-weight: 800;
            line-height: 1.45;
            color: var(--text-primary);
            margin-bottom: 14px;
            letter-spacing: -0.2px;
        }}
        .big-three-card.hero-lead .big-three-headline {{
            font-size: 19px;
        }}
        .why-it-matters-box {{
            background: rgba(0, 0, 0, 0.2);
            border-radius: var(--radius-sm);
            padding: 12px 14px;
            margin-bottom: 16px;
            flex-grow: 1;
        }}
        .box-label {{
            font-size: 10.5px;
            font-weight: 800;
            letter-spacing: 0.8px;
            color: var(--accent-cyan);
            margin-bottom: 4px;
            text-transform: uppercase;
        }}
        .box-content {{
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.6;
        }}
        .big-three-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--border-subtle);
            padding-top: 14px;
            margin-top: auto;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .metric-pill {{
            font-size: 11.5px;
            font-weight: 700;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}
        .link-btn-hero {{
            font-size: 12px;
            font-weight: 700;
            color: var(--accent-cyan);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.2s ease;
        }}
        .link-btn-hero:hover {{
            color: #ffffff;
            text-decoration: underline;
        }}

        /* --- 模組 5: 產業影響鏈 (Supply Chain Impact Matrix) --- */
        .impact-section {{
            margin-bottom: 30px;
        }}
        .impact-grid {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .impact-chain-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 16px 20px;
            display: grid;
            grid-template-columns: 1fr auto 1.2fr auto 1.4fr;
            align-items: center;
            gap: 16px;
            box-shadow: var(--shadow-subtle);
        }}
        .impact-node {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .node-badge {{
            font-size: 10.5px;
            font-weight: 800;
            letter-spacing: 0.6px;
            text-transform: uppercase;
        }}
        .trigger-node .node-badge {{ color: var(--accent-amber); }}
        .process-node .node-badge {{ color: var(--accent-cyan); }}
        .target-node .node-badge {{ color: var(--accent-green); }}
        .node-title {{
            font-size: 13px;
            color: var(--text-primary);
            line-height: 1.5;
            font-weight: 600;
        }}
        .highlighted-stocks {{
            color: var(--accent-green);
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
        }}
        .impact-arrow {{
            color: var(--text-dim);
            font-size: 16px;
            font-weight: 900;
        }}

        /* --- 快捷看盤看板 (Stats Bar) --- */
        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 14px;
            margin-bottom: 22px;
        }}
        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-left: 4px solid var(--card-accent, var(--accent-cyan));
            border-radius: var(--radius-md);
            padding: 14px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
            transition: all 0.25s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
            border-color: var(--card-accent, var(--accent-cyan));
            box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.35);
        }}
        .stat-info .stat-name {{
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 3px;
        }}
        .stat-info .stat-num {{
            font-size: 22px;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-primary);
            line-height: 1.1;
        }}
        .stat-unit {{
            font-size: 12px;
            font-weight: 500;
            color: var(--text-dim);
            margin-left: 2px;
        }}
        .stat-icon-wrapper {{
            font-size: 20px;
            width: 40px;
            height: 40px;
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        /* --- 工具列 (搜尋與篩選) --- */
        .toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
            margin-bottom: 26px;
            padding: 12px 18px;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-subtle);
            position: sticky;
            top: 10px;
            z-index: 99;
        }}
        .search-box {{
            flex: 1;
            min-width: 260px;
            position: relative;
        }}
        .search-input {{
            width: 100%;
            padding: 9px 14px 9px 38px;
            background: var(--bg-surface-elevated);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-sm);
            color: var(--text-primary);
            font-size: 13.5px;
            outline: none;
            transition: all 0.2s ease;
        }}
        .search-input:focus {{
            border-color: var(--accent-cyan);
            box-shadow: 0 0 14px rgba(56, 189, 248, 0.2);
        }}
        .search-icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-dim);
            font-size: 14px;
        }}
        .filter-tabs {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .tab-btn {{
            padding: 5px 14px;
            border-radius: 18px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid var(--border-subtle);
            background: var(--bg-surface-elevated);
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.2s ease;
            user-select: none;
        }}
        .tab-btn.active, .tab-btn:hover {{
            background: rgba(56, 189, 248, 0.16);
            color: var(--accent-cyan);
            border-color: var(--accent-cyan);
        }}

        /* --- 模組 6 & 7: 各大板塊與新聞卡片庫 --- */
        .category-section {{
            margin-bottom: 28px;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: var(--shadow-subtle);
        }}
        .section-header {{
            padding: 16px 22px;
            background: var(--bg-surface-elevated);
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
        }}
        .section-header:hover {{
            filter: brightness(1.05);
        }}
        .section-header-left {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .section-icon-box {{
            width: 38px;
            height: 38px;
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            border: 1px solid;
            flex-shrink: 0;
        }}
        .section-title {{
            font-size: 17px;
            font-weight: 800;
            letter-spacing: -0.2px;
        }}
        .section-subtitle {{
            display: block;
            font-size: 10.5px;
            font-weight: 600;
            color: var(--text-dim);
            letter-spacing: 0.8px;
        }}
        .section-count-badge {{
            padding: 2px 10px;
            border-radius: 14px;
            font-size: 11.5px;
            font-weight: 700;
            border: 1px solid;
            font-family: 'JetBrains Mono', monospace;
        }}
        .toggle-arrow {{
            color: var(--text-muted);
            font-size: 12px;
            transition: transform 0.3s ease;
        }}
        .toggle-arrow.collapsed {{
            transform: rotate(-90deg);
        }}

        /* 板塊一句話結論 (Sector Bottom Line) */
        .section-bottom-line-bar {{
            background: rgba(0, 0, 0, 0.15);
            border-bottom: 1px solid var(--border-subtle);
            padding: 10px 22px;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 12.5px;
        }}
        .bottom-line-tag {{
            font-weight: 800;
            font-size: 11px;
            flex-shrink: 0;
            letter-spacing: 0.5px;
        }}
        .bottom-line-text {{
            color: var(--text-secondary);
            font-weight: 500;
        }}

        .section-body {{
            padding: 20px;
            display: block;
        }}
        .section-body.collapsed {{
            display: none;
        }}

        /* 新聞卡片 Grid */
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
            gap: 16px;
        }}
        .news-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.25s ease;
        }}
        .news-card:hover {{
            border-color: var(--border-focus);
            transform: translateY(-2px);
            box-shadow: 0 10px 24px -5px rgba(0, 0, 0, 0.35);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .topic-tag {{
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: var(--radius-sm);
            border: 1px solid;
        }}
        .pub-time {{
            font-size: 11px;
            color: var(--text-dim);
            font-family: 'JetBrains Mono', monospace;
        }}
        .card-title {{
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 8px;
            line-height: 1.45;
            letter-spacing: -0.2px;
        }}

        /* 摘要展開/收合核心樣式 */
        .summary-wrapper {{
            margin-bottom: 12px;
            flex-grow: 1;
        }}
        .card-summary {{
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.65;
            transition: all 0.3s ease;
            word-break: break-word;
        }}
        .card-summary.clamped {{
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .expand-btn {{
            background: transparent;
            border: none;
            color: var(--accent-cyan);
            font-size: 11.5px;
            font-weight: 600;
            cursor: pointer;
            padding: 4px 0 0 0;
            margin-top: 2px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: color 0.2s;
            outline: none;
        }}
        .expand-btn:hover {{
            text-decoration: underline;
        }}

        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--border-subtle);
            padding-top: 10px;
            margin-top: 4px;
            font-size: 11.5px;
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
            padding: 3px 9px;
            border-radius: var(--radius-sm);
            border: 1px solid rgba(56, 189, 248, 0.2);
        }}
        .link-btn:hover {{
            background: var(--accent-cyan);
            color: #070b14;
        }}

        /* --- 模組 8 & 9: 雜訊速報 & 明日觀察清單 --- */
        .bottom-intel-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .bottom-intel-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 20px;
            box-shadow: var(--shadow-subtle);
        }}
        .bottom-intel-header {{
            font-size: 14px;
            font-weight: 800;
            letter-spacing: 0.5px;
            margin-bottom: 14px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .watchlist-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .watchlist-item {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.55;
        }}
        .watchlist-bullet {{
            font-size: 10.5px;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent-cyan);
            padding: 1px 6px;
            border-radius: 4px;
            flex-shrink: 0;
            margin-top: 2px;
        }}
        .noise-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .noise-item {{
            font-size: 12.5px;
            color: var(--text-muted);
            line-height: 1.5;
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}
        .noise-cat {{
            color: var(--accent-purple);
            font-weight: 600;
        }}
        .noise-title {{
            color: var(--text-secondary);
            text-decoration: none;
        }}
        .noise-title:hover {{
            color: var(--accent-cyan);
            text-decoration: underline;
        }}
        .noise-source {{
            color: var(--text-dim);
            font-size: 11.5px;
        }}

        /* --- 模組 10: 資料來源與金融合規免責聲明 --- */
        .footer-compliance {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 20px 24px;
            text-align: center;
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.7;
        }}
        .footer-sources {{
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--text-secondary);
        }}
        .footer-disclaimer {{
            font-size: 11px;
            color: var(--text-dim);
        }}

        /* --- 手機專屬底部浮動導航列 (Mobile Bottom Nav Bar) --- */
        .mobile-bottom-bar {{
            display: none;
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: rgba(14, 21, 38, 0.95);
            backdrop-filter: blur(16px);
            border-top: 1px solid var(--border-subtle);
            padding: 8px 16px;
            z-index: 999;
            justify-content: space-around;
            align-items: center;
        }}
        .bottom-nav-item {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 11px;
            font-weight: 600;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 3px;
            cursor: pointer;
            padding: 4px 8px;
        }}
        .bottom-nav-item:hover, .bottom-nav-item.active {{
            color: var(--accent-cyan);
        }}
        .bottom-nav-icon {{
            font-size: 16px;
        }}

        /* --- 列印與 PDF 匯出最佳化樣式 --- */
        @media print {{
            body {{
                background: #ffffff !important;
                color: #0f172a !important;
                background-image: none !important;
            }}
            .terminal-header, .sentiment-card, .big-three-card, .impact-chain-card, .category-section, .news-card, .bottom-intel-card, .footer-compliance {{
                background: #ffffff !important;
                border: 1px solid #cbd5e1 !important;
                box-shadow: none !important;
                color: #0f172a !important;
                break-inside: avoid;
            }}
            .header-title, .big-three-headline, .card-title, .node-title, .takeaway-text {{
                color: #0f172a !important;
            }}
            .toolbar, .header-actions, .toggle-arrow, .expand-btn, .mobile-bottom-bar {{
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

        /* --- RWD 斷點優化 --- */
        @media (max-width: 1024px) {{
            .big-three-grid {{
                grid-template-columns: 1fr;
            }}
            .impact-chain-card {{
                grid-template-columns: 1fr;
                gap: 8px;
            }}
            .impact-arrow {{
                text-align: center;
                transform: rotate(90deg);
            }}
            .bottom-intel-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 768px) {{
            .terminal-header {{
                flex-direction: column;
                align-items: flex-start;
                padding: 18px;
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
                padding-bottom: 4px;
            }}
            .mobile-bottom-bar {{
                display: flex;
            }}
            .container {{
                padding-bottom: 60px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 模組 1: 頂部金融終端 Header -->
        <header class="terminal-header" id="topHeader">
            <div class="header-title-area">
                <div class="brand-pill">
                    <span class="live-dot"></span>
                    SNAKE INTELLIGENCE · 決策級情報監測
                </div>
                <h1 class="header-title">Snake Daily Report</h1>
                <p class="header-subtitle">GLOBAL TECH & CAPITAL MARKETS TERMINAL · 全球科技與資本市場日報</p>
                <div class="header-meta-bar">
                    <span class="header-meta-item">📅 {display_date}</span>
                    <span class="header-meta-item">🕒 監測產出時間：{now_time_str}</span>
                    <span class="header-meta-item">📊 深度收錄：共 {total_count} 則關鍵情資</span>
                </div>
            </div>
            <div class="header-actions">
                <button class="btn" onclick="toggleTheme()" id="themeBtn" title="切換深色/淺色模式">🌓 切換外觀</button>
                <button class="btn btn-primary" onclick="toggleAllSummaries()">📖 展開/收合全部摘要</button>
                <button class="btn" onclick="toggleAllSections()">📂 展開/折疊板塊</button>
                <button class="btn" onclick="window.print()">🖨️ 列印/PDF</button>
            </div>
        </header>

        <!-- 模組 2: 今日一句話 (Executive Takeaway) -->
        <div class="takeaway-banner">
            <span class="takeaway-icon">💡</span>
            <div>
                <div class="takeaway-label">EXECUTIVE TAKEAWAY · 今日一句話核心定調</div>
                <div class="takeaway-text">{punchline}</div>
            </div>
        </div>

        <!-- 模組 3: 市場溫度與多空風向儀表板 (Market Sentiment) -->
        <section class="sentiment-section" id="sentimentSection">
            <div class="section-tag-header">
                <span class="section-tag-title">🌡️ 市場溫度與多空風向儀表板 (MARKET SENTIMENT & RISK PULSE)</span>
                <span style="font-size: 11px; color: var(--text-dim); font-family: 'JetBrains Mono', monospace;">REAL-TIME MULTI-DIMENSIONAL RADAR</span>
            </div>
            <div class="sentiment-grid">
                {sentiment_html}
            </div>
        </section>

        <!-- 模組 4: 今日必看 3 件事 (The Big 3 特刊頭條) -->
        <section class="big-three-section" id="bigThreeSection">
            <div class="section-tag-header">
                <span class="section-tag-title" style="color: var(--accent-cyan);">🔥 今日必看 3 件事 (THE BIG 3 · HEAVYWEIGHT CATALYSTS)</span>
                <span style="font-size: 11px; color: var(--text-dim); font-family: 'JetBrains Mono', monospace;">30-SECOND EXECUTIVE BRIEF</span>
            </div>
            <div class="big-three-grid">
                {big_three_html}
            </div>
        </section>

        <!-- 模組 5: 產業影響鏈矩陣 (Supply Chain Impact Matrix) -->
        <section class="impact-section" id="impactSection">
            <div class="section-tag-header">
                <span class="section-tag-title" style="color: var(--accent-green);">🔗 產業影響鏈矩陣 (SUPPLY CHAIN IMPACT MATRIX)</span>
                <span style="font-size: 11px; color: var(--text-dim); font-family: 'JetBrains Mono', monospace;">TRIGGER ➔ COMPONENT ➔ STOCKS</span>
            </div>
            <div class="impact-grid">
                {impact_html}
            </div>
        </section>

        <!-- 看盤統計看盤卡片 -->
        <div class="stats-bar">
            {stats_bar_html}
        </div>

        <!-- 工具列：即時關鍵字搜尋與分類快篩 -->
        <div class="toolbar" id="filterToolbar">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" class="search-input" placeholder="輸入關鍵字、主題、公司或股票代號（如：台積電、NVIDIA、聯準會、AI Agent）即時檢索..." oninput="filterNews()">
            </div>
            <div class="filter-tabs">
                {filter_tabs_html}
            </div>
        </div>

        <!-- 模組 6 & 7: 各大板塊新聞深度卡片庫 -->
        <div id="allSections">
            {sections_html}
        </div>

        <!-- 模組 8 & 9: 雜訊速讀 & 明日關鍵觀察指標 -->
        <div class="bottom-intel-grid">
            <div class="bottom-intel-card">
                <div class="bottom-intel-header" style="color: var(--accent-purple);">
                    <span>📡 今日市場雜訊與速報 (MARKET NOISE & QUICK HITS)</span>
                </div>
                <div class="noise-list">
                    {noise_html if noise_html else '<p style="font-size:12.5px; color:var(--text-dim);">今日無顯著次要雜訊，各篇情資均具備高度產業價值。</p>'}
                </div>
            </div>
            
            <div class="bottom-intel-card">
                <div class="bottom-intel-header" style="color: var(--accent-cyan);">
                    <span>🎯 明日關鍵觀察指標 (TOMORROW'S CATALYST WATCHLIST)</span>
                </div>
                <ul class="watchlist-list">
                    {watchlist_html}
                </ul>
            </div>
        </div>

        <!-- 模組 10: 資料來源與金融合規免責聲明 -->
        <footer class="footer-compliance">
            <div class="footer-sources">
                🌐 情報來源：彭博 (Bloomberg)、路透 (Reuters)、CNBC、工商時報、經濟日報、中央社、各大科技官方新聞稿與全球監管機構公告
            </div>
            <div class="footer-disclaimer">
                免責聲明 (Disclaimer)：本網站與日報所提供之所有資訊僅供科技產業動態研究與個人學術參考，不構成任何形式之投資邀約、推薦、買賣建議或金融顧問意見。投資涉及風險，證券價格可升可跌，請獨立評估或諮詢專業財務顧問。
            </div>
        </footer>
    </div>

    <!-- 手機端專屬底部浮動導航列 -->
    <nav class="mobile-bottom-bar">
        <button class="bottom-nav-item" onclick="scrollToElement('bigThreeSection')">
            <span class="bottom-nav-icon">🔥</span>
            <span>必看Top3</span>
        </button>
        <button class="bottom-nav-item" onclick="scrollToElement('impactSection')">
            <span class="bottom-nav-icon">🔗</span>
            <span>影響鏈</span>
        </button>
        <button class="bottom-nav-item" onclick="scrollToElement('filterToolbar')">
            <span class="bottom-nav-icon">📂</span>
            <span>分類篩選</span>
        </button>
        <button class="bottom-nav-item" onclick="scrollToElement('topHeader')">
            <span class="bottom-nav-icon">⬆️</span>
            <span>回頂端</span>
        </button>
    </nav>

    <!-- 前端互動與展開功能腳本 -->
    <script>
        // 深色 / 淺色主題切換與偏好記憶
        function initTheme() {{
            const savedTheme = localStorage.getItem('snake_report_theme') || 'dark';
            document.documentElement.setAttribute('data-theme', savedTheme);
            updateThemeButtonText(savedTheme);
        }}
        function toggleTheme() {{
            const current = document.documentElement.getAttribute('data-theme') || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('snake_report_theme', next);
            updateThemeButtonText(next);
        }}
        function updateThemeButtonText(theme) {{
            const btn = document.getElementById('themeBtn');
            if (btn) {{
                btn.innerText = theme === 'dark' ? '☀️ 淺色模式' : '🌙 深色模式';
            }}
        }}
        initTheme();

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
            
            sections.forEach(sec => {{
                if (catName === 'all' || sec.getAttribute('data-category') === catName) {{
                    sec.style.display = 'block';
                }} else {{
                    sec.style.display = 'none';
                }}
            }});
            
            filterNews();
        }}
        
        // 平滑滾動至指定錨點
        function scrollToElement(elemId) {{
            const el = document.getElementById(elemId);
            if (el) {{
                el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}
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

        // 即時關鍵字檢索
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
