"""Daily notification - email digest via QQ SMTP"""

import json
import os
import smtplib
import sys
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_project_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_articles():
    path = os.path.join(get_project_dir(), "data", "articles.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_html_digest(data, new_count):
    """Build an HTML email digest of today's changes"""
    articles = data.get("articles", [])
    total = data.get("total_articles", len(articles))
    now = datetime.now(timezone(timedelta(hours=8)))  # Beijing time
    date_str = now.strftime("%Y-%m-%d %H:%M")

    # Get truly new articles (those added by this scraper run)
    # Use the snapshot to determine what's new
    snapshot_path = os.path.join(get_project_dir(), "data", "url_snapshot.json")
    old_urls = set()
    if os.path.exists(snapshot_path):
        try:
            with open(snapshot_path, "r", encoding="utf-8") as f:
                snap = json.load(f)
                old_urls = set(snap.get("urls", []))
        except Exception:
            pass

    # Newest articles
    new_articles = [a for a in articles
                    if a.get("url", "").strip().lower().rstrip("/") not in old_urls
                    or not old_urls]  # no snapshot = first run, show recent

    # If no snapshot data, show the most recent articles
    if not old_urls and new_count == total:
        new_articles = articles[:15]  # show recent as "highlights"
    else:
        new_articles = new_articles[:20]

    # Recent high-relevance articles
    recent = sorted(articles, key=lambda a: a.get("relevance", 0), reverse=True)
    high_rel = [a for a in recent if a.get("relevance", 70) >= 70][:5]

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 640px; margin: 0 auto; background: #f5f5f5;">
<div style="background: linear-gradient(135deg, #1a73e8, #0d47a1); color: white; padding: 24px; border-radius: 8px 8px 0 0;">
  <h1 style="margin: 0; font-size: 22px;">APEC 2026 动态追踪</h1>
  <p style="margin: 8px 0 0; opacity: 0.9; font-size: 13px;">每日自动采集 · {date_str} (北京时间)</p>
</div>

<div style="background: white; padding: 20px; border-radius: 0 0 8px 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

  <div style="display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap;">
    <div style="flex: 1; min-width: 100px; background: #e8f5e9; padding: 12px; border-radius: 6px; text-align: center;">
      <div style="font-size: 28px; font-weight: bold; color: #2e7d32;">{new_count}</div>
      <div style="font-size: 12px; color: #666;">今日新增</div>
    </div>
    <div style="flex: 1; min-width: 100px; background: #e3f2fd; padding: 12px; border-radius: 6px; text-align: center;">
      <div style="font-size: 28px; font-weight: bold; color: #1565c0;">{total}</div>
      <div style="font-size: 12px; color: #666;">累计追踪</div>
    </div>
    <div style="flex: 1; min-width: 100px; background: #fff3e0; padding: 12px; border-radius: 6px; text-align: center;">
      <div style="font-size: 28px; font-weight: bold; color: #e65100;">{data.get('monthly_count', 0)}</div>
      <div style="font-size: 12px; color: #666;">本月新增</div>
    </div>
  </div>
"""

    if new_count == 0:
        html += """
  <div style="padding: 20px; text-align: center; color: #888;">
    <p style="font-size: 18px; margin: 0;">今日暂无新增动态</p>
    <p style="font-size: 13px; margin: 8px 0 0;">系统持续监控中，有更新会第一时间通知</p>
  </div>
"""
    else:
        html += f"""
  <h2 style="font-size: 16px; color: #333; border-bottom: 2px solid #1a73e8; padding-bottom: 6px;">今日新增 ({new_count}篇)</h2>
"""
        for a in new_articles[:15]:
            title = a.get("title", "无标题")[:80]
            url = a.get("url", "")
            source = a.get("source", "未知")
            date = a.get("date", "")
            rel = a.get("relevance", 50)
            cats = ", ".join(a.get("categories", ["其他"])[:2])
            emoji = "⭐" if rel >= 75 else "🔶" if rel >= 55 else "📄"
            html += f"""
  <div style="padding: 10px 0; border-bottom: 1px solid #eee;">
    <a href="{url}" style="color: #1a73e8; text-decoration: none; font-weight: 500; font-size: 14px;">{emoji} {title}</a>
    <div style="font-size: 12px; color: #888; margin-top: 4px;">
      {source} · {date} · 相关度 {rel} · <span style="background: #e8eaf6; padding: 1px 6px; border-radius: 3px;">{cats}</span>
    </div>
  </div>"""

        if len(new_articles) > 15:
            html += f"""
  <p style="color: #888; font-size: 13px; text-align: center;">... 共 {new_count} 篇新增文章</p>"""

    if high_rel and new_count > 0:
        html += f"""
  <h2 style="font-size: 16px; color: #333; border-bottom: 2px solid #e65100; padding-bottom: 6px; margin-top: 24px;">高相关度推荐</h2>
"""
        for a in high_rel:
            title = a.get("title", "无标题")[:80]
            url = a.get("url", "")
            rel = a.get("relevance", 70)
            html += f"""
  <div style="padding: 8px 0; border-bottom: 1px solid #eee;">
    <a href="{url}" style="color: #e65100; text-decoration: none; font-size: 14px;">⭐ {title}</a>
    <span style="font-size: 12px; color: #888; margin-left: 8px;">相关度 {rel}</span>
  </div>"""

    html += f"""
  <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid #eee; text-align: center;">
    <a href="https://xiaojing748.github.io/apec-tracker/" style="display: inline-block; background: #1a73e8; color: white; padding: 10px 24px; border-radius: 6px; text-decoration: none; font-weight: 500; margin: 4px;">查看完整看板</a>
    <a href="https://xiaojing748.github.io/apec-tracker/archive.html" style="display: inline-block; background: #f5f5f5; color: #333; padding: 10px 24px; border-radius: 6px; text-decoration: none; margin: 4px;">资料库</a>
  </div>

  <p style="font-size: 11px; color: #aaa; text-align: center; margin-top: 16px;">
    APEC 2026 动态追踪平台 · 自动采集 · 每日更新
  </p>
</div>
</body>
</html>"""
    return html


def build_plain_digest(data, new_count):
    """Build a plain-text email digest"""
    articles = data.get("articles", [])
    total = data.get("total_articles", len(articles))
    date_str = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")

    lines = [
        f"APEC 2026 动态追踪 — {date_str}",
        f"",
        f"今日新增: {new_count} 篇 | 累计: {total} 篇 | 本月: {data.get('monthly_count', 0)} 篇",
        f"",
    ]

    snapshot_path = os.path.join(get_project_dir(), "data", "url_snapshot.json")
    old_urls = set()
    if os.path.exists(snapshot_path):
        try:
            with open(snapshot_path, "r", encoding="utf-8") as f:
                snap = json.load(f)
                old_urls = set(snap.get("urls", []))
        except Exception:
            pass

    new_articles = [a for a in articles
                    if a.get("url", "").strip().lower().rstrip("/") not in old_urls
                    or not old_urls]
    if not old_urls and new_count == total:
        new_articles = articles[:10]
    else:
        new_articles = new_articles[:15]

    if new_count == 0:
        lines.append("今日暂无新增动态。系统持续监控中。")
    else:
        lines.append(f"--- 今日新增 ({new_count}篇) ---")
        for a in new_articles[:15]:
            title = (a.get("title", "")[:70] + "...") if len(a.get("title", "")) > 70 else a.get("title", "")
            rel = a.get("relevance", 50)
            star = "⭐" if rel >= 75 else "🔶" if rel >= 55 else "-"
            lines.append(f"{star} {title}")
            lines.append(f"   {a.get('source','')} · {a.get('date','')} · 相关度 {rel}")
            lines.append(f"   {a.get('url','')}")
            lines.append("")

    lines.extend([
        f"---",
        f"查看看板: https://xiaojing748.github.io/apec-tracker/",
        f"资料库: https://xiaojing748.github.io/apec-tracker/archive.html",
    ])
    return "\n".join(lines)


def send_email(sender, auth_code, receiver, subject, html_body, plain_body):
    """Send email via QQ SMTP (SSL). Bypass proxy since QQ SMTP is domestic."""
    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject

    msg.attach(MIMEText(plain_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # Temporarily clear proxy for domestic QQ SMTP
    old_http = os.environ.pop("HTTP_PROXY", None)
    old_https = os.environ.pop("HTTPS_PROXY", None)
    try:
        server = smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=30)
        server.login(sender, auth_code)
        server.sendmail(sender, [receiver], msg.as_string())
        server.quit()
        print("  Email sent successfully!")
        return True
    except Exception as e:
        print(f"  Email send failed: {e}")
        return False
    finally:
        if old_http:
            os.environ["HTTP_PROXY"] = old_http
        if old_https:
            os.environ["HTTPS_PROXY"] = old_https


def main():
    sender = os.environ.get("QQMAIL_SENDER", "")
    auth_code = os.environ.get("QQMAIL_AUTH_CODE", "")
    receiver = os.environ.get("QQMAIL_RECEIVER", sender)

    if not sender or not auth_code:
        print("  QQMAIL_SENDER or QQMAIL_AUTH_CODE not set, skipping email notification")
        sys.exit(0)

    print(f"  Sending daily digest to {receiver}...")

    try:
        data = load_articles()
    except Exception as e:
        print(f"  Failed to load articles: {e}")
        sys.exit(1)

    new_count = data.get("today_count", 0)
    total = data.get("total_articles", len(data.get("articles", [])))

    date_str = datetime.now(timezone(timedelta(hours=8))).strftime("%m/%d")

    if new_count == 0:
        subject = f"APEC 追踪 {date_str} | 今日无更新 · 累计 {total} 篇"
    elif new_count <= 3:
        subject = f"APEC 追踪 {date_str} | +{new_count} 篇新动态 · 累计 {total}"
    else:
        subject = f"APEC 追踪 {date_str} | +{new_count} 篇！累计 {total}"

    html_body = build_html_digest(data, new_count)
    plain_body = build_plain_digest(data, new_count)

    success = send_email(sender, auth_code, receiver, subject, html_body, plain_body)

    if success:
        print(f"  Notification sent: {subject}")


if __name__ == "__main__":
    main()
