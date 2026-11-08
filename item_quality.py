# -*- coding: utf-8 -*-
"""
Snake Daily Report - 新聞品質標記
統一判斷每則資料是否為備援內容、舊聞或僅有搜尋頁連結，
讓報表能如實標示，摘要分析也能排除不可信的項目。
"""
import re
from datetime import date, datetime

from config import GENERIC_URL_MARKERS, NEWS_MAX_AGE_DAYS

# 舊版程式產生的備援標題，用於辨識歷史快取中未帶 is_fallback 標記的項目
LEGACY_FALLBACK_MARKERS = ("最新產業趨勢與市場進展", "【焦點追蹤】", "最新重大進展")

_DATE_PATTERN = re.compile(r"(20\d{2})\s*[-/.年]\s*(\d{1,2})\s*[-/.月]\s*(\d{1,2})")


def is_fallback_item(item: dict) -> bool:
    """是否為未取得真實內容的備援項目（含舊版快取）"""
    if item.get("is_fallback"):
        return True
    title = item.get("title", "")
    return any(marker in title for marker in LEGACY_FALLBACK_MARKERS)


def is_generic_url(url: str) -> bool:
    """是否為搜尋結果頁，而非單篇新聞原文"""
    lowered = (url or "").lower()
    return any(marker in lowered for marker in GENERIC_URL_MARKERS)


def parse_publish_date(text: str, reference: date = None):
    """
    從發布時間文字取出日期。若為日期區間，取不晚於基準日的最新一天；
    無法辨識時回傳 None。
    """
    candidates = []
    for year, month, day in _DATE_PATTERN.findall(text or ""):
        try:
            candidates.append(date(int(year), int(month), int(day)))
        except ValueError:
            continue
    if not candidates:
        return None
    if reference:
        past = [d for d in candidates if d <= reference]
        if past:
            return max(past)
    return max(candidates)


def annotate_items(items: list, report_date: str) -> list:
    """為每則資料加上 is_fallback、is_search_link、is_stale、age_days 標記"""
    reference = datetime.strptime(report_date, "%Y%m%d").date()
    for item in items:
        item["is_fallback"] = is_fallback_item(item)
        url = item.get("url", "")
        item["is_search_link"] = bool(url) and is_generic_url(url)

        published = parse_publish_date(item.get("publish_time", ""), reference)
        age_days = (reference - published).days if published else None
        item["age_days"] = age_days
        item["is_stale"] = (
            not item["is_fallback"]
            and age_days is not None
            and age_days > NEWS_MAX_AGE_DAYS
        )
    return items
