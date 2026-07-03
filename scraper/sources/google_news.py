"""Google News RSS 采集器（不依赖API Key）"""

import re
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import feedparser
import requests

from scraper import config

# 搜索引擎/搜索页面域名（拒绝这些URL）
_SEARCH_DOMAINS = {
    "bing.com", "www.bing.com", "google.com", "www.google.com",
    "search.yahoo.com", "baidu.com", "www.baidu.com", "news.google.com",
}

# 不可靠的域名模式
_BAD_URL_PATTERNS = [
    r"/search\?q=", r"/search\?", r"bing\.com/search",
]


def search_all_keywords():
    """对所有关键词搜索 Google News RSS，批处理避免过多请求"""
    articles = []
    all_keywords = _collect_all_keywords()

    # Flatten and batch: search every keyword (no artificial limit)
    flat_keywords = []
    for kw_group, keywords in all_keywords.items():
        for kw in keywords:
            flat_keywords.append(kw)

    total = len(flat_keywords)
    print(f"      Google News: 共 {total} 个关键词，分组: {list(all_keywords.keys())}")

    # Combine into batch queries of ~3 keywords each to reduce requests
    batch_size = 3
    for i in range(0, len(flat_keywords), batch_size):
        batch = flat_keywords[i:i + batch_size]
        for kw in batch:
            results = _search_rss(kw)
            articles.extend(results)
        if i + batch_size < len(flat_keywords):
            time.sleep(1)  # rate-limit between batches

    return articles


def _search_rss(query):
    """通过 Google News RSS 搜索。
    自动加 APEC 限定词，确保结果聚焦 APEC 相关。
    """
    articles = []

    # 自动加 APEC 限定：如果关键词不含 APEC/亚太经合，自动加上
    ql = query.lower()
    if "apec" not in ql and "亚太经合" not in ql:
        query = f"APEC {query}"

    rss_url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"

    try:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            title = entry.get("title", "").strip()
            if " - " in title:
                title, source_name = title.rsplit(" - ", 1)
            else:
                source_name = "Google News"

            link = _extract_real_url(entry)
            if not link:
                continue

            summary = entry.get("summary", entry.get("description", ""))
            pub_date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            if not title:
                continue

            # 放宽域名过滤：不再丢弃非白名单域名，改为后续降权处理
            # 仅拒绝明确被屏蔽的域名
            domain = urlparse(link).netloc.lower().replace("www.", "")
            if domain in _SEARCH_DOMAINS:
                continue
            if domain in config.BLOCKED_DOMAINS or any(
                domain.endswith(d) for d in config.BLOCKED_DOMAINS
            ):
                continue

            # 多策略日期提取
            if not pub_date:
                pub_date = _extract_date_from_text(title + " " + (summary or ""))
            if not pub_date:
                pub_date = _extract_date_from_url(link)
            if not pub_date:
                # 兜底：用昨天的日期，不丢数据
                pub_date = datetime.now(timezone.utc) - timedelta(days=1)

            # 检查日期是否在合理范围内（不要未来日期，不要太久以前）
            now = datetime.now(timezone.utc)
            if pub_date > now:
                pub_date = now - timedelta(days=1)
            if pub_date < now - timedelta(days=180):
                continue  # 超过半年的旧闻不收录

            categories = config.classify_article(title, summary or "")
            articles.append({
                "title": title,
                "url": link,
                "source": source_name.strip(),
                "source_type": "权威媒体",
                "date": pub_date.strftime("%Y-%m-%d"),
                "summary": _clean_summary(summary)[:300] if summary else "",
                "categories": categories,
            })
    except Exception:
        pass

    return articles


def _extract_real_url(entry):
    """从Google News RSS条目中提取真实文章URL"""
    # feedparser会把真实URL放在link字段，但也可能包装成Google重定向
    link = entry.get("link", "").strip()

    # 如果是Google News重定向URL，尝试从参数中提取真实URL
    if "news.google.com/rss/articles" in link:
        parsed = urlparse(link)
        qs = parse_qs(parsed.query)
        real_url = qs.get("url", [None])[0]
        if real_url:
            link = real_url

    # 拒绝搜索引擎URL
    if not link:
        return ""
    domain = urlparse(link).netloc.lower().replace("www.", "")
    if domain in _SEARCH_DOMAINS:
        return ""
    for pattern in _BAD_URL_PATTERNS:
        if re.search(pattern, link):
            return ""

    return link


def _clean_summary(text):
    """清理摘要中的HTML标签"""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = re.sub(r"\s+", " ", clean)
    return clean.strip()


def _extract_date_from_text(text):
    """从文本提取日期，支持多种格式。返回 datetime 或 None。"""
    patterns = [
        # ISO dates: 2026-05-23, 2026/05/23, 2026.05.23
        r"\b(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})\b",
        # US dates: May 23, 2026 or May. 23, 2026
        r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2}),?\s*(20\d{2})\b",
        # Chinese dates: 2026年5月23日
        r"(20\d{2})年(\d{1,2})月(\d{1,2})日",
    ]
    months_map = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
                   "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                if m.re.pattern.startswith(r"\b(Jan"):
                    mon = months_map.get(m.group(1).lower()[:3], 1)
                    day = int(m.group(2))
                    year = int(m.group(3))
                elif "年" in m.re.pattern:
                    year, mon, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
                else:
                    year, mon, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
                if 2025 <= year <= 2027 and 1 <= mon <= 12 and 1 <= day <= 31:
                    return datetime(year, mon, day, tzinfo=timezone.utc)
            except (ValueError, IndexError):
                continue
    return None


def _extract_date_from_url(url):
    """从URL路径提取日期，如 /2026/05/23/ 或 /2026-05-23/"""
    m = re.search(r"/(20\d{2})[-/](\d{1,2})[-/](\d{1,2})[/-]", url)
    if m:
        try:
            y, mon, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if 2025 <= y <= 2027 and 1 <= mon <= 12 and 1 <= d <= 31:
                return datetime(y, mon, d, tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def _extract_year_date(text):
    """从文本提取年份，生成保守日期。只接受2025-2026年的。（保留兼容）"""
    years = re.findall(r"\b(20\d{2})\b", text)
    for y_str in sorted(years, reverse=True):
        y = int(y_str)
        if y < 2025 or y > 2026:
            continue
        return datetime(y, 1, 1, tzinfo=timezone.utc)
    return None


def _collect_all_keywords():
    """收集所有关键词，加入2026中国年关键词"""
    all_kw = dict(config.KEYWORDS)
    all_kw["2026中国年"] = config.CHINA_2026_KEYWORDS
    return all_kw
