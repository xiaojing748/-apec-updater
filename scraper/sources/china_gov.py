"""国内权威信源采集 - 外交部、新华社、国务院、人民网
直接搜索和采集国内政府/官方媒体，不依赖 Google News 中转。
"""

import json
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin, quote

import requests
from bs4 import BeautifulSoup

from scraper import config

SOURCES = [
    {
        "name": "新华社",
        "type": "权威媒体",
        "url": "http://so.news.cn/getNews",
        "params": {"keyword": "", "curPage": 1, "sortField": 0, "searchFields": 1, "lang": "cn"},
        "fmt": "json",
    },
    {
        "name": "人民网",
        "type": "权威媒体",
        "url": "http://search.people.com.cn/rmw/GB/rmwsearch/gj_search.jsp",
        "params": {"keyword": "", "st": 0},
        "fmt": "html",
    },
    {
        "name": "国务院",
        "type": "官方公告",
        "url": "http://sousuo.gov.cn/s.htm",
        "params": {"q": "", "t": "paper", "n": 20, "p": 0},
        "fmt": "html",
    },
    {
        "name": "外交部",
        "type": "官方公告",
        "url": "https://so.mfa.gov.cn/search/site",
        "params": {"q": "", "page": 0},
        "fmt": "html",
    },
]

SEARCH_KEYWORDS = [
    "APEC 网络安全",
    "APEC 数据跨境",
    "APEC 隐私保护",
    "APEC 数字经济",
    "APEC 贸易部长",
    "APEC 互联互通",
    "APEC 供应链",
    "APEC 中国年",
    "APEC 人工智能",
    "APEC 亚太经合",
]

CUTOFF_DAYS = 90


def fetch_all():
    articles = []
    for src in SOURCES:
        try:
            results = _fetch_source(src)
            articles.extend(results)
            print(f"        {src['name']}: {len(results)} 条")
        except Exception as e:
            print(f"        {src['name']} 采集出错: {e}")
    return articles


def _fetch_source(src):
    articles = []
    seen = set()
    cutoff = datetime.now(timezone.utc) - timedelta(days=CUTOFF_DAYS)
    for kw in SEARCH_KEYWORDS:
        try:
            params = dict(src["params"])
            for k in params:
                if isinstance(params[k], str) and params[k] == "":
                    if "keyword" in k.lower() or "searchword" in k.lower():
                        params[k] = kw
                    elif k in ("q", "query", "searchword"):
                        params[k] = kw
            if "keyword" in params:
                params["keyword"] = kw
            elif "q" in params:
                params["q"] = kw

            if src["fmt"] == "json":
                results = _parse_json(src, params, cutoff, seen)
            else:
                results = _parse_html(src, kw, params, cutoff, seen)
            articles.extend(results)
        except Exception:
            continue
    return articles


def _parse_json(src, params, cutoff, seen):
    articles = []
    try:
        resp = requests.get(src["url"], params=params, timeout=config.REQUEST_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (compatible; APECTracker/1.0)"})
        resp.raise_for_status()
        data = resp.json()
        items = []
        if isinstance(data, dict):
            items = data.get("content", {}).get("results", []) or data.get("results", [])
        elif isinstance(data, list):
            items = data
        for item in items[:15]:
            title = (item.get("title") or item.get("TITLE") or "").strip()
            url = (item.get("url") or item.get("URL") or "").strip()
            pub = _parse_date(item.get("pubtime") or item.get("PUBTIME") or item.get("date") or "")
            summary = (item.get("des") or item.get("DES") or item.get("summary") or "")[:300]
            if not title or not url or url in seen:
                continue
            if not pub:
                pub = _year_date(title + " " + summary, cutoff)
            if not pub or pub.replace(tzinfo=timezone.utc) < cutoff:
                continue
            seen.add(url)
            articles.append({
                "title": _clean(title), "url": url, "source": src["name"],
                "source_type": src["type"], "date": pub.strftime("%Y-%m-%d"),
                "summary": summary, "categories": config.classify_article(title, summary),
            })
    except Exception:
        pass
    return articles


def _parse_html(src, kw, params, cutoff, seen):
    articles = []
    try:
        resp = requests.get(src["url"], params=params, timeout=config.REQUEST_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (compatible; APECTracker/1.0)"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        selectors = [
            "li.news-item", "div.news-item", "div.result", "li.result",
            "div.searchresult", "li.searchresult", "div.list-item", "li.list-item",
            "div.item", "li.item", "div.news_list li", "ul.search-list li",
        ]
        items = []
        for sel in selectors:
            items = soup.select(sel)
            if items:
                break
        if not items:
            for tag in soup.select("li a[href], div a[href]"):
                p = tag.parent
                if p and p not in items:
                    items.append(p)
        for item in items[:10]:
            link = item.select_one("a[href]")
            if not link:
                continue
            url = urljoin(src["url"], link.get("href", ""))
            title = link.get_text(strip=True)
            if not title or len(title) < 8 or url in seen:
                continue
            date_el = item.select_one("span.date, span.time, .pub-date, .source-time, em")
            pub = _parse_date(date_el.get_text(strip=True)) if date_el else None
            if not pub:
                pub = _year_date(title, cutoff)
            if not pub or pub.replace(tzinfo=timezone.utc) < cutoff:
                continue
            summary_el = item.select_one("p, .des, .summary, .abstract")
            summary = summary_el.get_text(strip=True)[:300] if summary_el else ""
            seen.add(url)
            articles.append({
                "title": _clean(title), "url": url, "source": src["name"],
                "source_type": src["type"], "date": pub.strftime("%Y-%m-%d"),
                "summary": summary, "categories": config.classify_article(title, summary),
            })
    except Exception:
        pass
    return articles


def _parse_date(s):
    if not s:
        return None
    s = s.strip()
    for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d", "%Y年%m月%d日",
                "%Y年%m月%d日 %H:%M", "%m月%d日", "%d %B %Y", "%B %d, %Y"]:
        try:
            dt = datetime.strptime(s, fmt)
            if dt.year < 2000:
                dt = dt.replace(year=datetime.now().year)
            return dt
        except ValueError:
            continue
    return None


def _year_date(text, cutoff):
    for y_str in sorted(re.findall(r"\b(20\d{2})\b", text), reverse=True):
        y = int(y_str)
        if 2020 <= y <= 2026:
            c = datetime(y, 1, 1, tzinfo=timezone.utc)
            if c >= cutoff:
                return c
    return None


def _clean(title):
    title = re.sub(r"\s+", " ", title)
    for p in ["新华社", "人民网", "外交部", "国务院"]:
        for sep in ["：", ":"]:
            if title.startswith(p + sep):
                title = title[len(p)+1:].strip()
    return title[:200]