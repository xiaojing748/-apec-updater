"""Output module - merge results into data/articles.json + daily change tracking"""

import json
import os
import re
from datetime import datetime


def get_data_path():
    scraper_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(scraper_dir)
    data_dir = os.path.join(project_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "articles.json")


def get_snapshot_path():
    """Path to the URL snapshot file for change tracking"""
    scraper_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(scraper_dir)
    data_dir = os.path.join(project_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "url_snapshot.json")


def get_daily_report_path():
    """Path to the daily report markdown file"""
    scraper_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(scraper_dir)
    return os.path.join(project_dir, "daily-report.md")


def load_existing():
    path = get_data_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("articles", [])
        except (json.JSONDecodeError, KeyError):
            return []
    return []


def load_url_snapshot():
    """Load previously known URLs for change tracking"""
    path = get_snapshot_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError,):
            pass
    return {"urls": [], "timestamp": ""}


def save_url_snapshot(urls):
    """Save current URL set as snapshot for next run"""
    path = get_snapshot_path()
    data = {
        "urls": sorted(urls),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(urls),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def merge_articles(existing, new_articles):
    """Merge new articles with existing, dedupe by URL, preserve manual metadata"""
    merged = {}
    for a in existing:
        url = a.get("url", "").strip().lower().rstrip("/")
        if url:
            merged[url] = a
    for a in new_articles:
        url = a.get("url", "").strip().lower().rstrip("/")
        if url:
            if url in merged:
                # preserve manual edits (notes, starred) from existing
                old = merged[url]
                a.setdefault("notes", old.get("notes", ""))
                a.setdefault("starred", old.get("starred", False))
            merged[url] = a
    result = list(merged.values())
    result.sort(key=lambda x: x.get("date", ""), reverse=True)
    return result


def compute_changes(old_articles, new_articles):
    """Compare old vs new article lists, return list of truly new article URLs"""
    old_urls = set()
    for a in old_articles:
        url = a.get("url", "").strip().lower().rstrip("/")
        if url:
            old_urls.add(url)

    new_urls = set()
    for a in new_articles:
        url = a.get("url", "").strip().lower().rstrip("/")
        if url:
            new_urls.add(url)

    added_urls = new_urls - old_urls
    # Find the actual article objects for newly added URLs
    added = [a for a in new_articles
             if a.get("url", "").strip().lower().rstrip("/") in added_urls]

    # Find articles with metadata updates (same URL but changed relevance/categories)
    old_map = {}
    for a in old_articles:
        url = a.get("url", "").strip().lower().rstrip("/")
        if url:
            old_map[url] = a
    new_map = {}
    for a in new_articles:
        url = a.get("url", "").strip().lower().rstrip("/")
        if url:
            new_map[url] = a

    updated = []
    for url in new_urls & old_urls:
        old_a = old_map.get(url, {})
        new_a = new_map.get(url, {})
        if (old_a.get("relevance") != new_a.get("relevance") or
            set(old_a.get("categories", [])) != set(new_a.get("categories", [])) or
            old_a.get("summary", "") != new_a.get("summary", "")):
            # Metadata changed
            updated.append({
                "url": url,
                "title": new_a.get("title", ""),
                "old_relevance": old_a.get("relevance", 0),
                "new_relevance": new_a.get("relevance", 0),
                "old_categories": old_a.get("categories", []),
                "new_categories": new_a.get("categories", []),
            })

    return added, updated


def clean_old_year_articles(articles):
    current_year = datetime.now().year
    cleaned = []
    removed = 0
    for a in articles:
        title = a.get("title", "")
        date = a.get("date", "")
        years_in_title = [int(y) for y in re.findall(r"\b(20\d{2})\b", title)]
        if years_in_title:
            max_year = max(years_in_title)
            date_year = int(date[:4]) if date else current_year
            if max_year < date_year:
                removed += 1
                continue
        cleaned.append(a)
    if removed:
        print(f"  Cleaned {removed} old-year articles (title year mismatch)")
    return cleaned


def generate_daily_report(added, updated, total_articles, run_time=None):
    """Generate a daily report Markdown file"""
    if run_time is None:
        run_time = datetime.now()
    date_str = run_time.strftime("%Y-%m-%d")
    time_str = run_time.strftime("%H:%M")

    lines = []
    lines.append(f"# APEC 每日追踪报告 — {date_str}")
    lines.append(f"")
    lines.append(f"> 自动采集时间: {time_str} (北京时间) | 累计文章: {total_articles} 篇")
    lines.append(f"")

    if not added and not updated:
        lines.append("## 今日无更新")
        lines.append("")
        lines.append("今日未发现新的 APEC 相关动态。系统将持续监控。")
        lines.append("")
        lines.append(f"> 当前累计追踪 **{total_articles}** 篇 APEC 相关文章。")
    else:
        if added:
            lines.append(f"## 新增文章 ({len(added)} 篇)")
            lines.append("")
            # Group by category
            by_cat = {}
            for a in added:
                for cat in a.get("categories", ["其他"]):
                    by_cat.setdefault(cat, []).append(a)
            for cat in sorted(by_cat.keys()):
                articles = by_cat[cat]
                lines.append(f"### {cat} ({len(articles)} 篇)")
                lines.append("")
                for a in sorted(articles, key=lambda x: x.get("relevance", 0), reverse=True)[:20]:
                    rel = a.get("relevance", 50)
                    star = "⭐" if rel >= 75 else "🔶" if rel >= 55 else "📄"
                    title = a.get("title", "无标题")
                    url = a.get("url", "")
                    source = a.get("source", "未知")
                    date = a.get("date", "")
                    sq = a.get("source_quality", 4)
                    lines.append(f"- {star} **[{title}]({url})**")
                    lines.append(f"  - 来源: {source} | 日期: {date} | 相关度: {rel} | 质量: {sq}/10")
                if len(articles) > 20:
                    lines.append(f"  - ... 共 {len(articles)} 篇")
                lines.append("")

        if updated:
            lines.append(f"## 信息更新 ({len(updated)} 篇)")
            lines.append("")
            for u in updated[:20]:
                title = u.get("title", "无标题")
                old_r = u.get("old_relevance", 0)
                new_r = u.get("new_relevance", 0)
                direction = "↑" if new_r > old_r else "↓" if new_r < old_r else "→"
                lines.append(f"- 📝 **{title}**")
                lines.append(f"  - 相关度: {old_r} {direction} {new_r}")
                old_cats = ", ".join(u.get("old_categories", []))
                new_cats = ", ".join(u.get("new_categories", []))
                if old_cats != new_cats:
                    lines.append(f"  - 分类: {old_cats} → {new_cats}")
            if len(updated) > 20:
                lines.append(f"  - ... 共 {len(updated)} 篇有更新")
            lines.append("")

        lines.append("---")
        lines.append(f"> 📊 [查看完整看板](https://xiaojing748.github.io/apec-tracker/)")
        lines.append(f"> 📁 [资料库](https://xiaojing748.github.io/apec-tracker/archive.html)")

    report = "\n".join(lines)
    path = get_daily_report_path()
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Daily report written: {path}")
    return report


def write_json(articles, old_articles=None):
    path = get_data_path()
    articles = clean_old_year_articles(articles)

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    this_month = now.strftime("%Y-%m")

    monthly_count = sum(1 for a in articles if a.get("date", "").startswith(this_month))

    # Real change tracking: compare with old articles
    if old_articles is None:
        old_articles = load_url_snapshot().get("urls", [])
        old_url_set = set(old_articles)
        new_count = sum(
            1 for a in articles
            if a.get("url", "").strip().lower().rstrip("/") not in old_url_set
        )
    else:
        old_url_set = set(
            a.get("url", "").strip().lower().rstrip("/") for a in old_articles
        )
        new_count = sum(
            1 for a in articles
            if a.get("url", "").strip().lower().rstrip("/") not in old_url_set
        )

    # Save URL snapshot for next run
    current_urls = [a.get("url", "").strip().lower().rstrip("/") for a in articles if a.get("url")]
    save_url_snapshot(current_urls)

    output = {
        "last_updated": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": "Asia/Shanghai",
        "total_articles": len(articles),
        "today_count": new_count,  # now = truly new articles this run
        "year_count": sum(1 for a in articles if a.get("date", "").startswith("2026")),
        "monthly_count": monthly_count,
        "data_range": {
            "earliest": articles[-1].get("date", "") if articles else "",
            "latest": articles[0].get("date", "") if articles else "",
        },
        "articles": articles,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return path
