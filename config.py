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
    "AI": {
        "code": "A",
        "color": "#38bdf8",  # 霓虹天藍
        "icon": "🤖",
        "topics": [
            "AI Agent",
            "生成式AI模型",
            "多模態AI",
            "AI推論技術",
            "AI資料中心",
            "企業AI應用",
            "邊緣AI",
            "實體AI與機器人",
            "AI資安與治理",
            "開源AI生態"
        ]
    },
    "New technology": {
        "code": "B",
        "color": "#818cf8",  # 靛青紫
        "icon": "💻",
        "topics": [
            "量子運算",
            "人形機器人",
            "自動駕駛技術",
            "智慧眼鏡與XR",
            "先進半導體製程",
            "矽光子與CPO",
            "次世代電池技術",
            "衛星通訊與低軌衛星",
            "數位孿生技術",
            "Wi-Fi 8與6G通訊"
        ]
    },
    "投資市場": {
        "code": "C",
        "color": "#34d399",  # 翡翠綠
        "icon": "📈",
        "topics": [
            "全球主要股市指數",
            "全球央行利率政策",
            "美元指數",
            "主要貨幣匯率",
            "黃金與貴金屬",
            "原油與能源價格",
            "美國公債殖利率",
            "全球通膨數據",
            "加密貨幣市場",
            "地緣政治與市場風險"
        ]
    },
    "台灣股市": {
        "code": "D",
        "color": "#f472b6",  # 霓虹粉
        "icon": "⚡",
        "topics": [
            "台股加權指數",
            "三大法人買賣超",
            "外資買賣超",
            "台積電與半導體權值股",
            "AI伺服器供應鏈",
            "Notebook與ODM產業",
            "記憶體產業",
            "PCB與載板產業",
            "高股息與市值型ETF",
            "上市櫃公司營收與財報"
        ]
    },
    "美國股市": {
        "code": "E",
        "color": "#fbbf24",  # 琥珀金
        "icon": "🌱",
        "topics": [
            "美股四大指數",
            "美國科技七巨頭",
            "NVIDIA與AI晶片股",
            "費城半導體指數",
            "雲端運算公司",
            "AI軟體與資料分析公司",
            "電動車與自駕車產業",
            "美國企業財報",
            "華爾街分析師評級",
            "美股IPO與併購動態"
        ]
    }
}

def get_all_topics(categories=None):
    """
    展平為包含順序的題目列表。若有提供 categories (例如 ['A', 'C']) 則進行過濾。
    """
    items = []
    idx = 1
    for cat_name, cat_info in TOPIC_CATEGORIES.items():
        if categories and cat_info["code"] not in categories:
            continue
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
