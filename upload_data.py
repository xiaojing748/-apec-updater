"""数据上传脚本：将爬虫生成的 articles.json 上传到 COS

用法: python upload_data.py
前提: data/articles.json 已由爬虫生成
效果: 上传到 COS，网页自动加载最新数据（无需修改 HTML）
"""

import json
import os
import sys
from qcloud_cos import CosConfig, CosS3Client

REGION = os.environ.get("COS_REGION", "ap-beijing")
BUCKET = os.environ.get("COS_BUCKET", "apec-tracker-hajimi-2026-1449615649")
SECRET_ID = os.environ["COS_SECRET_ID"]
SECRET_KEY = os.environ["COS_SECRET_KEY"]

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "data", "articles.json")
COS_KEY = "data/articles.json"


def main():
    if not os.path.exists(DATA_FILE):
        print(f"ERROR: {DATA_FILE} not found")
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = data.get("total_articles", len(data.get("articles", [])))
    latest = data.get("data_range", {}).get("latest", "?")
    today = data.get("today_count", 0)
    print(f"[INFO] Uploading: {total} articles, +{today} new, latest: {latest}")

    config = CosConfig(Region=REGION, SecretId=SECRET_ID, SecretKey=SECRET_KEY)
    client = CosS3Client(config)

    body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    client.put_object(
        Bucket=BUCKET,
        Key=COS_KEY,
        Body=body,
        ContentType="application/json; charset=utf-8",
    )
    print(f"[OK] {COS_KEY} uploaded ({len(body):,} bytes)")
    print(f"访问: https://{BUCKET}.cos-website.{REGION}.myqcloud.com/")


if __name__ == "__main__":
    main()
