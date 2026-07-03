"""数据注入脚本：将新鲜 articles.json 注入 COS 上的 index.html
使用括号深度匹配算法精确替换 __APEC_DATA__ 块，不依赖正则。
"""

import json
import os
import sys
from qcloud_cos import CosConfig, CosS3Client

REGION = os.environ.get("COS_REGION", "ap-beijing")
BUCKET = os.environ.get("COS_BUCKET", "apec-tracker-hajimi-2026-1449615649")
SECRET_ID = os.environ["COS_SECRET_ID"]
SECRET_KEY = os.environ["COS_SECRET_KEY"]

# inject_data.py 在仓库根目录
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "data", "articles.json")


def main():
    if not os.path.exists(DATA_FILE):
        print(f"ERROR: {DATA_FILE} not found"); sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        fresh_data = json.load(f)

    total = fresh_data.get("total_articles", 0)
    print(f"[INFO] Fresh data: {total} articles")

    config = CosConfig(Region=REGION, SecretId=SECRET_ID, SecretKey=SECRET_KEY)
    client = CosS3Client(config)

    # 下载 COS HTML
    print("[INFO] Downloading index.html from COS...")
    resp = client.get_object(Bucket=BUCKET, Key="index.html")
    html = resp["Body"].get_raw_stream().read().decode("utf-8")
    print(f"[INFO] Downloaded {len(html):,} bytes")

    # 括号深度匹配替换
    marker = "window.__APEC_DATA__ = "
    pos = html.find(marker)
    if pos == -1:
        print("[ERROR] __APEC_DATA__ marker not found!"); sys.exit(1)

    brace_start = html.find("{", pos)
    if brace_start == -1:
        print("[ERROR] Opening brace not found!"); sys.exit(1)

    depth = 0
    in_string = False
    escape_next = False
    brace_end = -1
    for i in range(brace_start, len(html)):
        c = html[i]
        if escape_next:
            escape_next = False; continue
        if c == "\\":
            escape_next = True; continue
        if c == '"':
            in_string = not in_string; continue
        if in_string:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                brace_end = i; break

    if brace_end == -1:
        print("[ERROR] Closing brace not found!"); sys.exit(1)

    # 包含末尾的分号
    if brace_end + 1 < len(html) and html[brace_end + 1] == ";":
        brace_end += 1

    fresh_json = json.dumps(fresh_data, ensure_ascii=False)
    new_block = f"window.__APEC_DATA__ = {fresh_json};"
    old_len = brace_end + 1 - pos
    html = html[:pos] + new_block + html[brace_end + 1:]
    print(f"[INFO] Replaced block: {old_len:,} -> {len(new_block):,} chars")

    # 上传
    print(f"[INFO] Uploading ({len(html):,} bytes)...")
    client.put_object(Bucket=BUCKET, Key="index.html", Body=html.encode("utf-8"),
                      ContentType="text/html; charset=utf-8")
    print(f"[OK] COS updated: {total} articles")

    # 同时上传 JSON 备份
    client.put_object(Bucket=BUCKET, Key="data/articles.json",
                      Body=json.dumps(fresh_data, ensure_ascii=False, indent=2).encode("utf-8"),
                      ContentType="application/json; charset=utf-8")
    print("[OK] data/articles.json updated")


if __name__ == "__main__":
    main()
