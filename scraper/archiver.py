"""文章存档模块 - 下载全文并按日期归档为markdown + JSON索引，支持PDF报告下载"""
import json
import os
import re
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from scraper import config

ARCHIVE_DIR = None
INDEX_FILE = None


def _init_paths():
    global ARCHIVE_DIR, INDEX_FILE
    scraper_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(scraper_dir)
    ARCHIVE_DIR = os.path.join(project_dir, "docs", "archive", "docs")
    INDEX_FILE = os.path.join(project_dir, "docs", "archive", "index.json")
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)


def archive_all(articles, force=False):
    """归档所有文章：下载全文 → 保存markdown → 更新索引"""
    _init_paths()
    index_data = _load_index()
    existing_ids = {e["url"] for e in index_data.get("entries", [])}
    new_entries = []
    total = len(articles)
    success = 0

    for i, article in enumerate(articles):
        url = article.get("url", "")
        if not url or (url in existing_ids and not force):
            continue
        print(f"  [{i+1}/{total}] {article.get('title', '')[:60]}...")
        try:
            entry = _download_and_save(article)
            if entry:
                new_entries.append(entry)
                existing_ids.add(url)
                success += 1
            time.sleep(1.5)
        except Exception as e:
            print(f"        失败: {e}")

    all_entries = index_data.get("entries", []) + new_entries
    _update_index(all_entries)
    print(f"  归档完成: {success}/{total} 篇新增")
    return success


def _download_and_save(article):
    """下载单篇文章全文并保存为markdown，如有PDF报告则同时下载"""
    url = article.get("url", "")
    title = article.get("title", "无标题")
    date_str = article.get("date", datetime.now().strftime("%Y-%m-%d"))
    source = article.get("source", "")
    summary = article.get("summary", "")
    categories = article.get("categories", [])

    # 下载全文 + 检测PDF
    full_text, pdf_url = _fetch_article_text(url)

    slug = _slugify(title, 60)
    date_dir = os.path.join(ARCHIVE_DIR, date_str[:4], date_str[5:7], date_str[8:10])
    os.makedirs(date_dir, exist_ok=True)

    # 下载PDF（如果有）
    pdf_filename = ""
    if pdf_url:
        pdf_filename = f"{date_str}-{slug}.pdf"
        pdf_path = os.path.join(date_dir, pdf_filename)
        try:
            pdf_resp = requests.get(pdf_url, timeout=90, headers={
                "User-Agent": "Mozilla/5.0 (compatible; APECTracker/1.0)"
            })
            pdf_resp.raise_for_status()
            ct = pdf_resp.headers.get("Content-Type", "")
            if "pdf" in ct.lower() or len(pdf_resp.content) > 10000:
                with open(pdf_path, "wb") as f:
                    f.write(pdf_resp.content)
                print(f"        PDF已下载: {os.path.getsize(pdf_path)} bytes")
            else:
                pdf_filename = ""
        except Exception as e:
            print(f"        PDF下载失败: {e}")
            pdf_filename = ""

    if not full_text:
        full_text = f"*无法获取全文，请访问原文：{url}*"

    scraper_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # PDF下载链接
    NL = "\n"
    pdf_section = ""
    if pdf_filename:
        pdf_rel = os.path.relpath(os.path.join(date_dir, pdf_filename), scraper_dir).replace("\\", "/")
        pdf_section = f"{NL}{NL}## 报告PDF{NL}{NL}[📥 下载报告全文]({pdf_rel})"

    # PDF报告没有网页正文时
    if pdf_filename and (not full_text or "无法获取全文" in full_text):
        full_text = f"*本文章为PDF报告，请点击下方链接下载原文。*{NL}{NL}*原文链接: {url}*"

    md_filename = f"{date_str}-{slug}.md"
    md_path = os.path.join(date_dir, md_filename)

    md_content = (
        "---\n"
        f'title: "{title}"\n'
        f"date: {date_str}\n"
        f'source: "{source}"\n'
        f"categories: {json.dumps(categories, ensure_ascii=False)}\n"
        f'url: "{url}"\n'
        "---\n\n"
        f"# {title}\n\n"
        f"**来源:** {source}\n"
        f"**日期:** {date_str}\n"
        f"**分类:** {', '.join(categories)}\n"
        f"**原文链接:** [{url}]({url})\n\n"
        f"## 摘要\n\n"
        f"{summary if summary else '（无摘要）'}\n\n"
        f"## 全文\n\n"
        f"{full_text}"
        f"{pdf_section}\n"
    )

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    rel_path = os.path.relpath(md_path, scraper_dir).replace("\\", "/")
    pdf_rel_path = ""
    if pdf_filename:
        pdf_rel_path = os.path.relpath(os.path.join(date_dir, pdf_filename), scraper_dir).replace("\\", "/")

    return {
        "title": title,
        "date": date_str,
        "source": source,
        "categories": categories,
        "url": url,
        "file": rel_path,
        "pdf_file": pdf_rel_path,
        "has_fulltext": (full_text and "无法获取全文" not in full_text) or bool(pdf_filename),
    }


def _fetch_article_text(url):
    """下载网页正文，同时检测是否有PDF报告可下载
    Returns: (text, pdf_url_or_None)
    """
    try:
        resp = requests.get(url, timeout=config.REQUEST_TIMEOUT, headers={
            "User-Agent": "Mozilla/5.0 (compatible; APECTracker/1.0)"
        })
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # 检测PDF下载链接（APEC publication页面）
        pdf_url = None
        download_link = soup.select_one(".eyd-download-links, a[href*='publication/getfile']")
        if download_link:
            pdf_href = download_link.get("href", "")
            if pdf_href:
                pdf_url = urljoin(url, pdf_href)

        # 尝试多种正文选择器
        selectors = [
            "article", ".article-body", ".article-content", ".post-content",
            ".entry-content", ".content-body", "main", ".main-content",
            "#content", ".news-content", ".story-body",
        ]

        paragraphs = []
        for sel in selectors:
            container = soup.select_one(sel)
            if container:
                for tag in container.select("script, style, nav, .nav, .sidebar, .related"):
                    tag.decompose()
                paragraphs = [p.get_text(strip=True) for p in container.find_all("p")
                              if len(p.get_text(strip=True)) > 30]
                if paragraphs:
                    break

        if not paragraphs:
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")
                          if len(p.get_text(strip=True)) > 50]

        if paragraphs:
            return "\n\n".join(paragraphs[:30]), pdf_url

        return "", pdf_url
    except Exception:
        return "", None


def _load_index():
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError):
            pass
    return {"updated": "", "total": 0, "entries": []}


def _update_index(entries):
    entries.sort(key=lambda e: e.get("date", ""), reverse=True)
    index_data = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(entries),
        "entries": entries,
    }
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)


def _slugify(text, max_len=60):
    slug = re.sub(r"[^\w一-鿿-]", " ", text.lower())
    slug = re.sub(r"\s+", "-", slug).strip("-")
    return slug[:max_len]


def get_recent_archive_dates(days=30):
    _init_paths()
    index_data = _load_index()
    dates = set()
    cutoff = datetime.now().strftime("%Y-%m-%d")
    for e in index_data.get("entries", []):
        d = e.get("date", "")
        if d <= cutoff:
            dates.add(d)
    return sorted(dates, reverse=True)[:days]