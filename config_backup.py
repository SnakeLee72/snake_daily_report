# -*- coding: utf-8 -*-
"""
Snake Daily Report - 系統設定檔
定義 50 個主題清單、分類結構、Copilot 提示詞樣板與報表路徑設定
"""
import os
from pathlib import Path

# 基礎專案路徑
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

# 確保輸出目錄存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# 50 個分類主題完整定義清單
TOPIC_CATEGORIES = {
    "AI與科技": {
        "code": "A",
        "color": "#38bdf8",  # 霓虹天藍
        "icon": "🤖",
        "topics": [
            "OpenAI",
            "ChatGPT",
            "Gemini",
            "Claude",
            "Microsoft Copilot",
            "Google AI",
            "NVIDIA",
            "AMD",
            "Intel",
            "Apple"
        ]
    },
    "Notebook/ODM產業": {
        "code": "B",
        "color": "#818cf8",  # 靛青紫
        "icon": "💻",
        "topics": [
            "Lenovo",
            "HP",
            "Dell",
            "ASUS",
            "Acer",
            "Compal",
            "Quanta",
            "Wistron",
            "Inventec",
            "Camera Module產業"
        ]
    },
    "投資市場": {
        "code": "C",
        "color": "#34d399",  # 翡翠綠
        "icon": "📈",
        "topics": [
            "台股加權指數",
            "美股四大指數",
            "台積電",
            "特斯拉",
            "亞馬遜",
            "Google",
            "Meta",
            "Broadcom",
            "Oracle",
            "三大法人",
            "外資買賣超",
            "美元指數",
            "台幣匯率",
            "黃金",
            "美國利率相關資訊"
        ]
    },
    "開發技術": {
        "code": "D",
        "color": "#f472b6",  # 霓虹粉
        "icon": "⚡",
        "topics": [
            "Python",
            "FastAPI",
            "Streamlit",
            "PyInstaller",
            "Godot Engine",
            "AI Agent",
            "Claude Code",
            "Codex",
            "Gemini CLI",
            "VS Code"
        ]
    },
    "個人成長": {
        "code": "E",
        "color": "#fbbf24",  # 琥珀金
        "icon": "🌱",
        "topics": [
            "健康研究",
            "長壽研究",
            "心理學",
            "商業思維",
            "商用英文"
        ]
    }
}

def get_all_topics():
    """
    展平為包含順序的 50 個題目列表
    """
    items = []
    idx = 1
    for cat_name, cat_info in TOPIC_CATEGORIES.items():
        for topic in cat_info["topics"]:
            items.append({
                "id": idx,
                "category": cat_name,
                "category_code": cat_info["code"],
                "topic": topic
            })
            idx += 1
    return items

# Copilot 365 專用結構化提問樣板（要求回覆標準格式以便正則擷取）
COPILOT_PROMPT_TEMPLATE = (
    "請搜尋並提供關於「{topic}」的最新1則重大新聞或最新動態資訊。\n"
    "請嚴格依照以下格式輸出（不要多餘的問候語，也不要重覆這段提示規範）：\n"
    "【類別】：{category}\n"
    "【主題】：{topic}\n"
    "【標題】：（請提供繁體中文新聞或動態標題）\n"
    "【摘要】：（請以繁體中文撰寫，100字以內精華摘要）\n"
    "【來源】：（報導媒體、官方機構或資訊來源）\n"
    "【發布時間】：（報導日期或時間）\n"
    "【原始連結】：（報導網址或搜尋來源）"
)

# 系統設定
SETTINGS = {
    # 預設 Edge 執行檔路徑 (Windows 11)
    "EDGE_PATH": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    
    # 郵件 SMTP 設定（可由環境變數注入）
    "SMTP_SERVER": os.getenv("SNAKE_SMTP_SERVER", "smtp.gmail.com"),
    "SMTP_PORT": int(os.getenv("SNAKE_SMTP_PORT", 587)),
    "SMTP_USER": os.getenv("SNAKE_SMTP_USER", ""),
    "SMTP_PASS": os.getenv("SNAKE_SMTP_PASS", ""),
    "EMAIL_SENDER": os.getenv("SNAKE_EMAIL_SENDER", ""),
    "EMAIL_RECEIVERS": [r.strip() for r in os.getenv("SNAKE_EMAIL_RECEIVERS", "").split(",") if r.strip()],
    
    # LLM API 設定（可由環境變數注入）
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
}
