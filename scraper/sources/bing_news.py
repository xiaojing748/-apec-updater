"""Bing News Search API 采集器"""

from datetime import datetime, timedelta, timezone

import requests

from scraper import config


def search_all_keywords():
    """对所有关键词组合执行Bing News搜索"""
    if not config.BING_API_KEY:
        return []

    articles = []
    all_keywords = _collect_all_keywords()

    for kw_group, keywords in all_keywords.items():
        for kw in keywords[:3]:  # 每组关键词只取前3个，控制API调用量
            results = _search_bing(kw)
            articles.extend(results)

    return articles


def _search_bing(query):
    """调用 Bing News Search API"""
    articles = []
    url = "https://api.bing.microsoft.com/v7.0/news/search"
    headers = {"Ocp-Apim-Subscription-Key": config.BING_API_KEY}
    params = {
        "q": query,
        "count": 10,
        "freshness": "Week",
        "mkt": "en-US",
        "sortBy": "Date",
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("value", []):
            title = item.get("name", "").strip()
            article_url = item.get("url", "").strip()
            description = item.get("description", "").strip()
            pub_date = item.get("datePublished", "")[:10]
            provider = item.get("provider", [{}])[0].get("name", "Bing News")

            if not title or not article_url:
                continue
            if not _is_allowed_domain(article_url):
                continue

            categories = config.classify_article(title, description)
            articles.append({
                "title": title,
                "url": article_url,
                "source": provider,
                "source_type": "权威媒体",
                "date": pub_date[:10] if pub_date else datetime.now().strftime("%Y-%m-%d"),
                "summary": description[:300] if description else "",
                "categories": categories,
            })
    except Exception:
        pass

    return articles


def _collect_all_keywords():
    """收集所有关键词，加入2026中国年关键词"""
    all_kw = dict(config.KEYWORDS)
    all_kw["2026中国年"] = config.CHINA_2026_KEYWORDS
    return all_kw


_SEARCH_DOMAINS = {
    "bing.com", "www.bing.com", "google.com", "www.google.com",
    "search.yahoo.com", "baidu.com", "www.baidu.com",
}


def _is_allowed_domain(url):
    """检查URL域名是否在白名单（拒绝搜索引擎域名）"""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.lower().replace("www.", "")
    if domain in _SEARCH_DOMAINS or "/search" in url.lower():
        return False
    return domain in config.ALLOWED_DOMAINS or any(
        domain.endswith(d) for d in config.ALLOWED_DOMAINS
    )
