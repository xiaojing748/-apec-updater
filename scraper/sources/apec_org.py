"""APEC 官方网站爬虫 - 使用原始XML解析RSS，不依赖feedparser"""

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from scraper import config


def fetch_news():
    """从 APEC 官网 RSS 和新闻页面获取最新文章"""
    articles = []
    articles.extend(_fetch_rss())
    articles.extend(_fetch_news_page())
    return articles


def _fetch_rss():
    """使用原始XML解析APEC RSS Feed"""
    articles = []
    rss_url = "https://www.apec.org/feeds/rss"
    cutoff = datetime.now(timezone.utc) - timedelta(days=config.MAX_DAYS_LOOKBACK)

    try:
        resp = requests.get(rss_url, timeout=config.REQUEST_TIMEOUT, headers={
            "User-Agent": "Mozilla/5.0 (compatible; APECTracker/1.0)"
        })
        resp.raise_for_status()

        root = ET.fromstring(resp.text)
        ns = {"a10": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//item")
        print(f"        RSS: {rss_url} -> {len(items)} items")

        for item in items:
            title = ""
            link = ""
            pub_date = None
            summary = ""

            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            date_el = item.find("pubDate")

            if title_el is not None and title_el.text:
                title = title_el.text.strip()
            if link_el is not None and link_el.text:
                link = link_el.text.strip()
            if desc_el is not None and desc_el.text:
                summary = _clean_html(desc_el.text)
            if date_el is not None and date_el.text:
                try:
                    pub_date = parsedate_to_datetime(date_el.text.strip())
                except Exception:
                    pass

            if not title or not link:
                continue

            # 如果没有解析到日期，尝试从标题或URL中提取年份
            if not pub_date:
                pub_date = _extract_date_from_text(title + " " + link, cutoff)
            if not pub_date:
                continue  # 无法确定日期的跳过，不用今天代替

            if pub_date < cutoff:
                continue

            date_str = pub_date.strftime("%Y-%m-%d")
            categories = config.classify_article(title, summary)

            articles.append({
                "title": title,
                "url": link,
                "source": "APEC官网",
                "source_type": "官方公报",
                "date": date_str,
                "summary": summary[:300] if summary else "",
                "categories": categories,
            })

        print(f"        RSS after filter: {len(articles)} articles")

    except Exception as e:
        print(f"        RSS parse error: {e}")

    return articles


def _fetch_news_page():
    """从 APEC 新闻列表页面补充抓取"""
    articles = []
    news_urls = [
        "https://www.apec.org/news",
        "https://www.apec.org/publications",
    ]
    cutoff = datetime.now(timezone.utc) - timedelta(days=config.MAX_DAYS_LOOKBACK)

    for url in news_urls:
        try:
            resp = requests.get(url, timeout=config.REQUEST_TIMEOUT, headers={
                "User-Agent": "Mozilla/5.0 (compatible; APECTracker/1.0)"
            })
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            for item in soup.select("article, .news-item, .publication-item, .card, .list-item"):
                link_el = item.select_one("a[href]")
                date_el = item.select_one("time, .date, .published")

                title_el = item.select_one("h2 a, h3 a, h4 a, .title a")
                if not title_el:
                    title_el = item.select_one("h2, h3, h4, .title")
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                # 去掉常见前缀（分类标签被拼接到标题的情况）
                for prefix in ["Reports", "Press Release", "News", "Statement"]:
                    if title.startswith(prefix) and len(title) > len(prefix) + 1:
                        title = title[len(prefix):].strip()
                link = ""
                if link_el:
                    link = urljoin(url, link_el.get("href", ""))
                pub_date = None
                if date_el:
                    pub_date = _parse_date(date_el.get_text(strip=True))
                if not pub_date:
                    pub_date = _extract_date_from_text(title + " " + link, cutoff)

                if not title or not link:
                    continue
                if not pub_date:
                    continue
                if pub_date.replace(tzinfo=timezone.utc) < cutoff:
                    continue

                categories = config.classify_article(title)
                articles.append({
                    "title": title,
                    "url": link,
                    "source": "APEC官网",
                    "source_type": "官方公报",
                    "date": pub_date.strftime("%Y-%m-%d"),
                    "summary": "",
                    "categories": categories,
                })
        except Exception:
            continue

    return articles


def _extract_date_from_text(text, cutoff):
    """从文本中提取年份，生成一个保守的日期（该年1月1日）。
    如果年份不在cutoff范围内，返回None。"""
    import re as _re
    years = _re.findall(r"\b(20\d{2})\b", text)
    for y_str in sorted(years, reverse=True):
        y = int(y_str)
        if y < 2020 or y > 2026:
            continue
        candidate = datetime(y, 1, 1, tzinfo=timezone.utc)
        if candidate >= cutoff:
            return candidate
    return None


def _clean_html(html_text):
    if not html_text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", html_text)
    clean = re.sub(r"\s+", " ", clean)
    return clean.strip()


def _parse_date(date_str):
    formats = [
        "%Y-%m-%d", "%d %B %Y", "%B %d, %Y", "%d/%m/%Y",
        "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return datetime.now()
