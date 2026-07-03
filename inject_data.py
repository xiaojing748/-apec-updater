"""数据注入脚本：将新鲜 articles.json 注入 COS 上的 index.html

用法: python inject_data.py
前提: data/articles.json 已由爬虫生成
效果: 替换 COS index.html 中的 __APEC_DATA__ 块，保持 SPA 结构不变
"""

import json
import os
import re
import sys
from qcloud_cos import CosConfig, CosS3Client

# ====== 配置（通过环境变量传入，不写死在代码里）======
REGION = os.environ.get("COS_REGION", "ap-beijing")
BUCKET = os.environ.get("COS_BUCKET", "apec-tracker-hajimi-2026-1449615649")
SECRET_ID = os.environ["COS_SECRET_ID"]
SECRET_KEY = os.environ["COS_SECRET_KEY"]

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "data", "articles.json")
INDEX_KEY = "index.html"
DATA_KEY = "data/articles.json"


def main():
    # 1. 读取新鲜数据
    if not os.path.exists(DATA_FILE):
        print(f"ERROR: {DATA_FILE} not found")
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        fresh_data = json.load(f)

    total = fresh_data.get("total_articles", len(fresh_data.get("articles", [])))
    latest = fresh_data.get("data_range", {}).get("latest", "?")
    print(f"[INFO] Fresh data: {total} articles, latest: {latest}")

    # 2. 连接 COS
    config = CosConfig(Region=REGION, SecretId=SECRET_ID, SecretKey=SECRET_KEY)
    client = CosS3Client(config)

    # 3. 下载当前 COS index.html
    print(f"[INFO] Downloading {INDEX_KEY} from COS...")
    resp = client.get_object(Bucket=BUCKET, Key=INDEX_KEY)
    html = resp["Body"].get_raw_stream().read().decode("utf-8")
    print(f"[INFO] Downloaded {len(html):,} bytes")

    # 4. 替换 __APEC_DATA__ 块（用括号匹配，精确找到结束位置）
    fresh_json = json.dumps(fresh_data, ensure_ascii=False)
    new_block = f"window.__APEC_DATA__ = {fresh_json};"

    start_marker = "window.__APEC_DATA__ = "
    pos = html.find(start_marker)
    if pos == -1:
        print("[ERROR] Could not find __APEC_DATA__ marker in HTML!")
        sys.exit(1)

    # 找到 JSON 起始的 {
    brace_start = html.find("{", pos)
    if brace_start == -1:
        print("[ERROR] Could not find opening brace after __APEC_DATA__")
        sys.exit(1)

    # 括号深度匹配，找到匹配的 }
    depth = 0
    in_string = False
    escape_next = False
    brace_end = -1
    for i in range(brace_start, len(html)):
        c = html[i]
        if escape_next:
            escape_next = False
            continue
        if c == '\\':
            escape_next = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                brace_end = i
                break

    if brace_end == -1:
        print("[ERROR] Could not find matching closing brace!")
        sys.exit(1)

    # 确认后面是 ;
    if html[brace_end + 1:brace_end + 2] == ';':
        brace_end += 1

    old_block = html[pos:brace_end + 1]
    html = html[:pos] + new_block + html[brace_end + 1:]
    print(f"[INFO] Replaced __APEC_DATA__ block "
          f"(old: {len(old_block):,} chars, new: {len(new_block):,} chars)")

    # 5. 上传更新后的 index.html
    print(f"[INFO] Uploading {INDEX_KEY} ({len(html):,} bytes)...")
    client.put_object(
        Bucket=BUCKET,
        Key=INDEX_KEY,
        Body=html.encode("utf-8"),
        ContentType="text/html; charset=utf-8",
    )
    print(f"[OK] {INDEX_KEY} updated")

    # 6. 同时更新 data/articles.json（供 API 访问）
    print(f"[INFO] Uploading {DATA_KEY}...")
    client.put_object(
        Bucket=BUCKET,
        Key=DATA_KEY,
        Body=json.dumps(fresh_data, ensure_ascii=False, indent=2).encode("utf-8"),
        ContentType="application/json; charset=utf-8",
    )
    print(f"[OK] {DATA_KEY} updated")

    print(f"\n[DONE] COS 已更新：{total} 篇文章，截止 {latest}")
    print(f"访问: https://{BUCKET}.cos-website.{REGION}.myqcloud.com/")


if __name__ == "__main__":
    main()
