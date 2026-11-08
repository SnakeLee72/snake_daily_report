# -*- coding: utf-8 -*-
"""
Snake Daily Report - 每日分析引擎 (Summarizer)
所有分析內容都必須來自當日新聞清單：
1. Copilot 模式：在同一聊天室追加一題，請 Copilot 根據清單產出分析
2. Cache 模式：沿用當日已存檔的分析結果
3. 有設定金鑰時，可改用 Gemini / OpenAI
4. 以上皆無法使用時，只從新聞挑選必看 3 則；其餘分析區塊留空，由報表隱藏
"""
import json
import re
import urllib.request
from datetime import datetime

from config import DATA_DIR, SETTINGS, TOPIC_CATEGORIES

# 請 Copilot 分析時，每則摘要最多帶入的字數，避免提問過長
PROMPT_SUMMARY_CHARS = 60

SOURCE_LABELS = {
    "copilot": "Microsoft 365 Copilot",
    "gemini": "Gemini",
    "openai": "OpenAI",
}


def generate_ai_summary(news_items: list, mode: str = "copilot", report_date: str = None) -> dict:
    """根據當日新聞產出分析；無法產出時回傳只含必看 3 則的結果"""
    report_date = report_date or datetime.now().strftime("%Y%m%d")

    if mode == "copilot":
        try:
            print("[AI 摘要] 正在同一聊天室請 Copilot 產出今日分析...")
            result = generate_copilot_analysis(news_items, report_date)
            if result:
                return result
            print("[AI 摘要警告] 未取得可用的 Copilot 分析")
        except Exception as e:
            print(f"[AI 摘要警告] Copilot 分析失敗: {e}")

    # 重新產出報表，或這次 Copilot 分析失敗時，沿用今日已存檔的結果
    cached = _load_saved_analysis(report_date)
    if cached:
        print("[AI 摘要] 沿用今日已存檔的分析結果")
        return cached

    for source, api_key, call_api in (
        ("gemini", SETTINGS.get("GEMINI_API_KEY"), _call_gemini_api),
        ("openai", SETTINGS.get("OPENAI_API_KEY"), _call_openai_api),
    ):
        if not api_key:
            continue
        try:
            print(f"[AI 摘要] 正在調用 {SOURCE_LABELS[source]} API 生成今日分析...")
            result = _normalize_analysis(call_api(news_items, api_key, report_date), news_items, source)
            _save_analysis(result, report_date)
            return result
        except Exception as e:
            print(f"[AI 摘要警告] {SOURCE_LABELS[source]} API 調用失敗: {e}")

    print("[AI 摘要] 本次沒有 AI 分析，報表僅列出新聞內容")
    return _build_news_only_summary(news_items)


def generate_copilot_analysis(news_items: list, report_date: str):
    """在 Copilot 聊天室追加分析題，成功時存檔並回傳分析結果"""
    from copilot_collector import ask_copilot_once

    def is_valid(text: str) -> bool:
        return "你是科技與資本市場分析師" not in text and _parse_analysis_json(text) is not None

    prompt = _build_summary_prompt(news_items, report_date)
    reply = ask_copilot_once(prompt, is_valid)
    if not reply:
        return None

    try:
        result = _normalize_analysis(_parse_analysis_json(reply), news_items, "copilot")
    except ValueError as e:
        debug_file = DATA_DIR / f"ai_summary_raw_{report_date}.txt"
        debug_file.write_text(reply, encoding="utf-8")
        print(f"[AI 摘要警告] {e}，原始回覆已存至 {debug_file}")
        return None

    _save_analysis(result, report_date)
    return result


def _analysis_file(report_date: str):
    return DATA_DIR / f"ai_summary_{report_date}.json"


def _save_analysis(result: dict, report_date: str):
    with open(_analysis_file(report_date), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def _load_saved_analysis(report_date: str):
    path = _analysis_file(report_date)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        print(f"[AI 摘要警告] 讀取已存檔分析失敗: {e}")
        return None


def _parse_analysis_json(text: str):
    """從回覆取出 JSON 物件，容許程式碼區塊與結尾多餘逗號；失敗回傳 None"""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    body = re.sub(r",\s*([}\]])", r"\1", text[start:end + 1])
    try:
        data = json.loads(body, strict=False)
    except ValueError:
        return None
    return data if isinstance(data, dict) and "the_big_three" in data else None


def _build_summary_prompt(news_items: list, report_date: str) -> str:
    """組裝分析提問；只帶入真實取得的新聞，並要求不得使用清單以外的資訊"""
    lines = []
    for item in news_items:
        if item.get("is_fallback"):
            continue
        summary = item.get("summary", "")[:PROMPT_SUMMARY_CHARS]
        stale_mark = "（舊聞）" if item.get("is_stale") else ""
        lines.append(
            f"{item.get('id')}. [{item.get('category')}/{item.get('topic')}] "
            f"{item.get('title')}｜{summary}｜{item.get('publish_time') or '日期未標示'}{stale_mark}"
        )
    news_text = "\n".join(lines)

    display_date = f"{report_date[:4]}-{report_date[4:6]}-{report_date[6:]}"
    sector_lines = ",\n".join(f'    "{name}": "本類別今日重點一句話"' for name in TOPIC_CATEGORIES)

    return f"""你是科技與資本市場分析師。今天是 {display_date}。請只根據下方新聞清單整理今日重點。
規則：
1. 不可使用清單以外的資訊，不可編造數字、日期、公司或事件。
2. 標註「舊聞」的項目不可當成今日事件。
3. 資料不足時，文字欄位留空字串，清單欄位留空陣列。
4. 只輸出一段合法 JSON，不要加說明文字、引用標記或 Markdown。

新聞清單（編號. [分類/主題] 標題｜摘要｜發布日）：
{news_text}

JSON 格式：
{{
  "punchline": "一句話總結今日最重要的趨勢",
  "market_sentiment": {{
    "tech_momentum": {{"status": "四字以內狀態", "desc": "依據清單的一句話說明", "trend": "up、down 或 neutral"}},
    "capital_flow": {{"status": "四字以內狀態", "desc": "依據清單的一句話說明", "trend": "up、down 或 neutral"}},
    "supply_chain": {{"status": "四字以內狀態", "desc": "依據清單的一句話說明", "trend": "up、down 或 neutral"}},
    "risk_level": {{"status": "四字以內狀態", "desc": "依據清單的一句話說明", "trend": "up、down 或 neutral"}}
  }},
  "the_big_three": [
    {{"rank": 1, "news_id": 1, "why_it_matters": "為什麼這則最重要", "key_metric": "新聞中的實際數字，沒有就留空"}},
    {{"rank": 2, "news_id": 2, "why_it_matters": "為什麼重要", "key_metric": ""}},
    {{"rank": 3, "news_id": 3, "why_it_matters": "為什麼重要", "key_metric": ""}}
  ],
  "sector_bottom_lines": {{
{sector_lines}
  }},
  "impact_chain": [
    {{"trigger": "清單中的驅動事件", "impacted_area": "受影響的產業環節", "key_beneficiaries": "新聞中明確提到的公司，沒有就留空"}}
  ],
  "tomorrow_watchlist": ["清單中明確提到、近期將發生的事件"],
  "market_noise": [4, 5]
}}
news_id 與 market_noise 請填新聞清單的編號；market_noise 放次要的例行消息。"""


def _clean_text(value) -> str:
    return value.strip() if isinstance(value, str) else ""


def _normalize_analysis(data: dict, news_items: list, source: str) -> dict:
    """
    將模型回覆整理成報表欄位。必看新聞以編號對回真實資料，
    標題與連結一律取自新聞本身，查無編號的項目會被捨棄。
    """
    usable_items = {
        str(item.get("id")): item for item in news_items if not item.get("is_fallback")
    }

    big_three = []
    for entry in data.get("the_big_three") or []:
        item = usable_items.get(str(entry.get("news_id"))) if isinstance(entry, dict) else None
        if not item:
            continue
        big_three.append({
            "rank": len(big_three) + 1,
            "category": item.get("category", ""),
            "topic": item.get("topic", ""),
            "headline": item.get("title", ""),
            "why_it_matters": _clean_text(entry.get("why_it_matters")) or item.get("summary", ""),
            "key_metric": _clean_text(entry.get("key_metric")),
            "url": item.get("url", ""),
        })
        if len(big_three) == 3:
            break

    punchline = _clean_text(data.get("punchline"))
    if not punchline or not big_three:
        raise ValueError("分析回覆缺少一句話總結或必看新聞")

    sentiment = {}
    for key, value in (data.get("market_sentiment") or {}).items():
        if isinstance(value, dict) and _clean_text(value.get("status")):
            sentiment[key] = {
                "status": _clean_text(value.get("status")),
                "desc": _clean_text(value.get("desc")),
                "trend": _clean_text(value.get("trend")) or "neutral",
            }

    sector_lines = {
        name: _clean_text(text)
        for name, text in (data.get("sector_bottom_lines") or {}).items()
        if name in TOPIC_CATEGORIES and _clean_text(text)
    }

    impact_chain = [
        {
            "trigger": _clean_text(entry.get("trigger")),
            "impacted_area": _clean_text(entry.get("impacted_area")),
            "key_beneficiaries": _clean_text(entry.get("key_beneficiaries")),
        }
        for entry in data.get("impact_chain") or []
        if isinstance(entry, dict) and _clean_text(entry.get("trigger"))
    ]

    watchlist = [_clean_text(w) for w in data.get("tomorrow_watchlist") or [] if _clean_text(w)]

    market_noise = []
    for news_id in data.get("market_noise") or []:
        item = usable_items.get(str(news_id))
        if item:
            market_noise.append({
                "title": item.get("title", ""),
                "category": item.get("category", ""),
                "source": item.get("source", ""),
                "url": item.get("url", ""),
            })

    return {
        "analysis_source": source,
        "punchline": punchline,
        "market_sentiment": sentiment,
        "the_big_three": big_three,
        "sector_bottom_lines": sector_lines,
        "impact_chain": impact_chain,
        "tomorrow_watchlist": watchlist[:4],
        "market_noise": market_noise[:5],
    }


def _call_gemini_api(news_items: list, api_key: str, report_date: str) -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = _build_summary_prompt(news_items, report_date)

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.3
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=35) as resp:
        res_json = json.loads(resp.read().decode("utf-8"))
        text = res_json["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text.strip())


def _call_openai_api(news_items: list, api_key: str, report_date: str) -> dict:
    url = "https://api.openai.com/v1/chat/completions"
    prompt = _build_summary_prompt(news_items, report_date)

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Output pure valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.3
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    })
    with urllib.request.urlopen(req, timeout=35) as resp:
        res_json = json.loads(resp.read().decode("utf-8"))
        text = res_json["choices"][0]["message"]["content"]
        return json.loads(text.strip())


def _build_news_only_summary(news_items: list) -> dict:
    """沒有 AI 分析時，只依關鍵字挑出必看 3 則，內容全部取自新聞本身"""
    scored = []
    for item in news_items:
        if item.get("is_fallback"):
            continue
        text = item.get("title", "") + " " + item.get("summary", "")
        score = 0
        if any(w in text for w in ["億", "併購", "收購", "大漲", "創歷史", "突破", "聯準會", "降息", "產能全滿"]):
            score += 3
        if any(w in text for w in ["NVIDIA", "台積電", "OpenAI", "Google", "蘋果", "微軟"]):
            score += 2
        if item.get("is_stale"):
            score -= 5
        scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    big_three = []
    for rank, (_, item) in enumerate(scored[:3], 1):
        text = item.get("title", "") + " " + item.get("summary", "")
        metrics = list(dict.fromkeys(re.findall(r"\d+(?:\.\d+)?(?:億美元|億元|%|點|萬人|家)", text)))
        big_three.append({
            "rank": rank,
            "category": item.get("category", ""),
            "topic": item.get("topic", ""),
            "headline": item.get("title", ""),
            "why_it_matters": item.get("summary", ""),
            "key_metric": " · ".join(metrics[:2]),
            "url": item.get("url", ""),
        })

    return {
        "analysis_source": None,
        "punchline": "",
        "market_sentiment": {},
        "the_big_three": big_three,
        "sector_bottom_lines": {},
        "impact_chain": [],
        "tomorrow_watchlist": [],
        "market_noise": [],
    }
