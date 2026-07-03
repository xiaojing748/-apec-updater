"""APEC 动态追踪 - 主爬虫入口
GitHub Actions 每天调用此脚本，采集 → 过滤 → 增量合并 → 输出JSON + 每日报告
"""

import os
import sys
import time
from datetime import datetime

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.sources import apec_org, bing_news, google_news, china_gov
from scraper.filters import apply as apply_filters
from scraper.output import (load_existing, merge_articles, write_json,
                              compute_changes, generate_daily_report)


def main():
    print(f"[{datetime.now()}] APEC动态追踪采集开始...")

    # 加载历史数据（变更追踪用）
    existing = load_existing()
    print(f"  已有 {len(existing)} 条历史数据")

    all_articles = []

    # 1. APEC 官网（RSS + HTML）
    print("  [1/4] 采集 APEC 官网...")
    try:
        apec_results = apec_org.fetch_news()
        print(f"        获取 {len(apec_results)} 条")
        all_articles.extend(apec_results)
        time.sleep(2)
    except Exception as e:
        print(f"        APEC官网采集出错: {e}")

    # 2. Google News RSS（无需API Key，总是可用）
    print("  [2/4] 采集 Google News...")
    try:
        google_results = google_news.search_all_keywords()
        print(f"        获取 {len(google_results)} 条")
        all_articles.extend(google_results)
        time.sleep(2)
    except Exception as e:
        print(f"        Google News采集出错: {e}")

    # 3. Bing News API（仅在配置了API Key时使用）
    print("  [3/4] 采集 Bing News...")
    try:
        bing_results = bing_news.search_all_keywords()
        print(f"        获取 {len(bing_results)} 条")
        all_articles.extend(bing_results)
    except Exception as e:
        print(f"        Bing News采集出错: {e}")

    # 4. 国内权威信源（外交部、新华社、国务院、人民网等）
    print("  [4/4] 采集国内权威信源...")
    try:
        china_results = china_gov.fetch_all()
        print(f"        获取 {len(china_results)} 条")
        all_articles.extend(china_results)
    except Exception as e:
        print(f"        国内信源采集出错: {e}")

    # 过滤：去重 → 域名过滤 → 关键词匹配 → 质量过滤 → 元数据增强
    print(f"\n  采集完成，共 {len(all_articles)} 条（过滤前）")
    new_filtered = apply_filters(all_articles)
    print(f"  过滤后 {len(new_filtered)} 条新数据")

    # 增量合并：新旧数据合并，按URL去重
    all_filtered = merge_articles(existing, new_filtered)

    # 跟踪真实变更
    added, updated = compute_changes(existing, all_filtered)
    print(f"  合并完成: +{len(added)}新增, ~{len(updated)}更新, 总计 {len(all_filtered)} 条")

    # 写入JSON（含真实 new_count）
    write_json(all_filtered, old_articles=existing)

    # 生成每日报告
    report = generate_daily_report(added, updated, len(all_filtered))
    print(f"  每日报告已生成")

    # 归档文章全文
    print("\n  归档文章全文...")
    from scraper.archiver import archive_all
    try:
        archive_all(all_filtered)
    except Exception as e:
        print(f"  归档出错（非致命）: {e}")

    print(f"[{datetime.now()}] 采集完成！")
    print(f"  新增: {len(added)}, 更新: {len(updated)}, 累计: {len(all_filtered)}")


if __name__ == "__main__":
    main()
