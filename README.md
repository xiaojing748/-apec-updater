# APEC Tracker 自动更新系统

每天北京时间 08:00 自动采集 APEC 网络安全与数字经济动态，
注入到腾讯云 COS 静态网站，保持看板数据每日更新。

## 工作原理

```
GitHub Actions (每天08:00)
  ├─ 运行爬虫 → 采集 APEC 官网 / Google News / Bing News
  ├─ 生成 data/articles.json
  ├─ 下载 COS index.html → 替换 __APEC_DATA__ → 上传回 COS
  └─ 网站 https://xxx.cos-website.ap-beijing.myqcloud.com 自动更新
```

## 部署

1. Fork 本仓库
2. 在 Settings → Secrets → Actions 添加：
   - `COS_SECRET_ID`: 腾讯云 SecretId
   - `COS_SECRET_KEY`: 腾讯云 SecretKey
3. 手动触发一次 Actions → "Daily APEC Update" → Run workflow
4. 之后每天自动运行
