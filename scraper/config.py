"""APEC Tracking - Configuration v3
项目基准: 多边平台网络安全相关合作进展研究 → APEC平台 × 网络安全交叉面
"""
# ============================================================
# 搜索关键词 — Google News / Bing 采集用
# ============================================================
KEYWORDS = {
    # ---- 核心层: 项目硬要求 ----
    "数据跨境与隐私保护": [
        "APEC CBPR", "Global CBPR Forum", "CBPR 2.0", "Cross-Border Privacy Rules",
        "APEC cross-border data flow", "APEC cross border data",
        "APEC data privacy framework", "APEC data privacy subgroup",
        "APEC data protection", "APEC data certification",
        "APEC personal information protection", "APEC personal data protection",
        "APEC privacy framework", "APEC privacy protection",
        "APEC data breach notification", "APEC sensitive data",
        "APEC data localization", "APEC data sovereignty",
        "APEC data adequacy", "APEC data free flow with trust",
        "APEC trusted data flow",
        "APEC 跨境数据流动", "APEC 数据跨境", "APEC 数据隐私", "APEC 数据保护",
        "APEC 个人信息保护", "APEC 隐私框架", "APEC 隐私保护",
        "APEC 数据本地化", "APEC 数据主权", "APEC 数据有序流动", "APEC 数据出境",
        "APEC DDTP", "APEC DFFT",
    ],
    "AI安全治理": [
        "APEC AI governance", "APEC AI safety",
        "APEC artificial intelligence governance",
        "APEC artificial intelligence safety",
        "APEC AI ethics", "APEC responsible AI",
        "APEC AI framework", "APEC AI regulation",
        "APEC AI standard", "APEC AI standards rivalry",
        "APEC AI US China", "APEC AI Initiative 2026",
        "APEC 人工智能治理", "APEC 人工智能安全", "APEC 人工智能标准",
        "APEC AI 治理", "APEC AI 安全",
        "APEC TELWG AI", "APEC telecom AI",
        "APEC digital week AI", "APEC digital minister AI",
    ],
    "电信与网络治理": [
        "APEC TELWG", "APEC TEL WG", "APEC Telecommunications Working Group",
        "APEC DESG", "APEC ECSG", "APEC TELMIN", "APEC ICT Minister",
        "APEC cybersecurity", "APEC network security",
        "APEC cybercrime", "APEC cyber crime",
        "APEC CERT", "APEC CSIRT", "APEC incident response",
        "APEC CIIP", "APEC critical information infrastructure",
        "APEC critical infrastructure protection",
        "APEC 5G security", "APEC ICT security",
        "APEC telecom security", "APEC communications security",
        "APEC cloud security",
        "APEC 网络安全", "APEC 网络犯罪", "APEC 网络攻击",
        "APEC 关键信息基础设施", "APEC 关基保护",
        "APEC 电信安全", "APEC 通信安全", "APEC 5G安全",
        "APEC 电信工作组", "APEC 数字经济转向组",
    ],
    # ---- 交叉层: 项目分析维度 ----
    "数字贸易规则": [
        "APEC digital trade rules", "APEC digital economy rules",
        "APEC AIDER", "APEC digital economy roadmap",
        "APEC digital trade barrier", "APEC data-driven trade",
        "APEC 数字贸易规则", "APEC 数字经济规则",
        "APEC digital trade", "APEC paperless trade",
        "APEC digital services regulation",
    ],
    "地缘安全博弈": [
        "APEC cybersecurity cooperation", "APEC cybersecurity tension",
        "APEC digital sovereignty", "APEC tech decoupling",
        "APEC cyber deterrence", "APEC cyber norms",
        "APEC cybersecurity US China", "APEC cybersecurity rivalry",
        "APEC FTAAP", "APEC trade security",
        "APEC economic security", "APEC economic coercion",
        "APEC multilateral security", "APEC security governance",
        "APEC 网络安全合作", "APEC 数字主权",
        "APEC 经济安全", "APEC 安全治理",
    ],
    # ---- 辅助层 ----
    "2026中国年": [
        "APEC 2026 China", "APEC China 2026", "APEC host year 2026",
        "APEC China host", "APEC 2026 host economy",
        "APEC 2026 中国", "APEC 2026 中国年", "APEC 2026 主办",
        "APEC 深圳 2026", "APEC Shenzhen 2026",
        "APEC Shanghai 2026", "APEC Suzhou 2026",
        "APEC Harbin 2026", "APEC Dalian 2026", "APEC Chengdu 2026",
        "APEC 上海", "APEC 苏州", "APEC 哈尔滨", "APEC 大连", "APEC 成都", "APEC 深圳",
    ],
}

CHINA_2026_KEYWORDS = [
    "APEC 2026 China", "APEC China 2026", "APEC host year 2026",
    "APEC China host", "APEC 2026 host economy",
    "APEC 2026 中国", "APEC 2026 中国年", "APEC 2026 主办",
    "APEC Suzhou", "APEC Shanghai", "APEC Harbin", "APEC Dalian",
    "APEC Chengdu", "APEC Shenzhen",
    "APEC 苏州", "APEC 上海", "APEC 哈尔滨", "APEC 大连", "APEC 成都", "APEC 深圳",
    "APEC Beijing 2026", "APEC 北京 2026",
]

# ============================================================
# 分类匹配 — classify_article()
# ============================================================
CORE_MATCH = {
    "数据跨境与隐私保护": [
        "dps", "cbpr", "cross-border privacy", "cross border data",
        "data privacy", "data protection", "data flow",
        "data sovereignty", "data localization", "data adequacy",
        "privacy framework", "privacy shield",
        "personal data", "personal information",
        "dfft", "data free flow with trust",
        "跨境数据", "数据跨境", "数据隐私", "数据保护",
        "个人信息", "隐私保护", "隐私框架", "数据主权", "数据出境",
    ],
    "AI安全治理": [
        "ai governance", "ai safety", "ai standard",
        "ai ethic", "ai regulation", "ai framework",
        "responsible ai", "artificial intelligence governance",
        "ai initiative", "ai adoption safety",
        "人工智能治理", "人工智能安全", "人工智能标准",
        "AI治理", "AI安全", "AI伦理", "AI标准",
    ],
    "电信与网络治理": [
        "telwg", "desg", "ecsg", "telmin",
        "telecommunications working group",
        "telecom security", "telecom standard",
        "digital economy steering", "data privacy subgroup",
        "ict minister",
        "ciip", "critical information infrastructure",
        "cybersecurity", "cyber security", "cybercrime", "cyber crime",
        "cert", "csirt", "incident response",
        "5g security", "ict security", "cloud security",
        "network security", "电信安全", "通信安全", "5g安全",
        "网络安全", "网络犯罪", "网络攻击",
        "电信工作组", "数字经济转向组",
        "关键信息基础设施", "关基保护",
    ],
    "数字贸易规则": [
        "digital trade rule", "digital economy rule",
        "digital trade", "digital economy roadmap",
        "aider", "data certification",
        "digital services regulation", "digital governance",
        "digital trade barrier", "data-driven trade",
        "数字贸易规则", "数字经济规则", "数字贸易",
        "数字治理", "数据认证", "数字贸易", "数据壁垒",
    ],
    "地缘安全博弈": [
        "mrt", "cti", "ftaap", "multilateral", "多边",
        "cybersecurity cooperation", "cybersecurity tension",
        "digital sovereignty", "tech decoupling",
        "cyber deterrence", "cyber norms",
        "economic security", "economic coercion",
        "multilateral security", "security governance",
        "网络安全合作", "数字主权", "经济安全",
        "安全治理", "科技脱钩", "网络规范",
    ],
}

CHINA_MATCH = [
    "som1", "som2", "som3", "som 1", "som 2",
    "shanghai", "harbin", "dalian", "chengdu", "shenzhen",
    "host year", "china 2026", "abac",
    "中国年", "哈尔滨", "上海", "大连", "成都", "深圳",
    "mrt", "digital week", "ceo summit",
    "贸易部长", "数字周", "领导人", "峰会",
]

CATEGORY_ORDER = [
    "数据跨境与隐私保护", "AI安全治理", "电信与网络治理",
    "数字贸易规则", "地缘安全博弈", "2026中国年", "其他APEC动态",
]

# ============================================================
# Domain Whitelist / Blacklist
# ============================================================
ALLOWED_DOMAINS = [
    "apec.org", "www.apec.org",
    "oecd.org", "www.oecd.org", "wto.org", "www.wto.org",
    "csis.org", "www.csis.org", "eastwestcenter.org",
    "pecc.org", "www.pecc.org",
    "xinhuanet.com", "www.xinhuanet.com", "news.cn", "www.news.cn",
    "people.com.cn", "en.people.cn",
    "gov.cn", "www.gov.cn", "mfa.gov.cn", "www.mfa.gov.cn",
    "cac.gov.cn", "www.cac.gov.cn",
    "cctv.com", "www.cctv.com",
    "chinanews.com", "www.chinanews.com", "chinadaily.com.cn",
    "globaltimes.cn", "www.globaltimes.cn",
    "reuters.com", "www.reuters.com", "ap.org", "apnews.com",
    "bloomberg.com", "www.bloomberg.com",
    "thediplomat.com", "www.thediplomat.com",
    "scmp.com", "www.scmp.com", "asia.nikkei.com",
    "straitstimes.com", "www.straitstimes.com",
    "channelnewsasia.com", "www.channelnewsasia.com",
    "thejakartapost.com", "www.thejakartapost.com",
    "koreaherald.com", "www.koreaherald.com",
    "japantimes.co.jp", "www.japantimes.co.jp",
    "bangkokpost.com", "www.bangkokpost.com",
    "ft.com", "www.ft.com", "wsj.com", "www.wsj.com",
    "economist.com", "www.economist.com",
    "bbc.com", "www.bbc.com", "cnn.com", "www.cnn.com",
    "washingtonpost.com", "www.washingtonpost.com",
    "nytimes.com", "www.nytimes.com",
    "brookings.edu", "www.brookings.edu", "cfr.org", "www.cfr.org",
    "iiss.org", "www.iiss.org",
    "theregister.com", "www.theregister.com",
    "theverge.com", "www.theverge.com", "techcrunch.com", "www.techcrunch.com",
    "wired.com", "www.wired.com", "arstechnica.com", "www.arstechnica.com",
    "cyberscoop.com", "www.cyberscoop.com", "darkreading.com", "www.darkreading.com",
    "iapp.org", "www.iapp.org",
    "state.gov", "www.state.gov", "commerce.gov", "www.commerce.gov",
    "whitehouse.gov", "www.whitehouse.gov",
    "dfat.gov.au", "www.dfat.gov.au", "mofa.go.jp", "www.mofa.go.jp",
]

BLOCKED_DOMAINS = [
    "facebook.com", "twitter.com", "x.com", "reddit.com",
    "youtube.com", "instagram.com", "tiktok.com", "linkedin.com",
    "wikipedia.org", "zhihu.com", "weibo.com",
]

REQUEST_TIMEOUT = 30
REQUEST_DELAY = 2
MAX_ARTICLES_PER_SOURCE = 50
MAX_DAYS_LOOKBACK = 150
BING_API_KEY = ""

# ============================================================
# 元数据提取规则
# ============================================================
DOC_TYPE_RULES = [
    ("official_statement", ["joint statement", "ministerial statement", "declaration",
         "联合声明", "部长声明", "宣言", "communique", "公报"]),
    ("press_release", ["press release", "news release", "新闻稿", "发布"]),
    ("meeting_minutes", ["meeting", "minutes", "summary record", "会议", "纪要"]),
    ("policy_document", ["policy", "framework", "guideline", "roadmap", "strategy",
         "政策", "框架", "指南", "路线图", "战略", "white paper", "白皮书"]),
    ("report", ["report", "analysis", "review", "assessment", "outlook",
         "报告", "分析", "评估", "展望", "trends"]),
    ("speech", ["speech", "remarks", "address", "keynote", "演讲", "致辞", "讲话"]),
    ("regulation", ["regulation", "rule", "standard", "law", "act",
         "法规", "规则", "标准", "法案"]),
    ("media_report", ["news", "coverage", "报道", "新闻"]),
    ("academic", ["paper", "journal", "research", "study", "学术", "研究"]),
]

APEC_BODY_RULES = [
    ("TELWG", ["telwg", "tel wg", "telecommunications working group", "电信工作组"]),
    ("DESG", ["desg", "digital economy steering group", "数字经济转向组"]),
    ("ECSG", ["ecsg", "e-commerce steering group", "电子商务转向组"]),
    ("DPS", ["dps", "data privacy subgroup", "数据隐私小组"]),
    ("SOM", ["som", "senior officials", "soms", "高官会"]),
    ("MRT", ["mrt", "ministers responsible for trade", "贸易部长"]),
    ("ABAC", ["abac", "business advisory council", "工商咨询理事会"]),
    ("CTI", ["cti", "committee on trade", "贸易投资委员会"]),
    ("TELMIN", ["telmin", "telecommunications minister", "ict minister", "数字经济部长"]),
]

GEO_RULES = [
    ("china", ["china", "chinese", "beijing", "shanghai", "中国", "北京", "上海",
         "哈尔滨", "大连", "成都", "深圳"]),
    ("usa", ["united states", "america", "us ", "washington", "美国", "华盛顿"]),
    ("japan", ["japan", "japanese", "tokyo", "日本", "东京"]),
    ("korea", ["korea", "korean", "seoul", "韩国", "首尔"]),
    ("asean", ["asean", "southeast asia", "vietnam", "thailand", "indonesia",
         "东南亚", "东盟"]),
    ("australia", ["australia", "australian", "澳大利亚"]),
    ("russia", ["russia", "russian", "俄罗斯"]),
    ("canada", ["canada", "canadian", "加拿大"]),
    ("latin_america", ["chile", "peru", "mexico", "拉丁美洲", "智利", "秘鲁", "墨西哥"]),
    ("global", ["global", "multilateral", "international", "全球", "多边"]),
]

POLICY_TAG_RULES = [
    ("CBPR", ["cbpr", "cross border privacy rules", "跨境隐私规则"]),
    ("AIDER", ["aider", "digital economy roadmap", "数字经济路线图"]),
    ("DFFT", ["dfft", "data free flow with trust", "可信数据自由流动"]),
    ("FTAAP", ["ftaap", "free trade area asia pacific", "亚太自贸区"]),
    ("DEPA", ["depa", "digital economy partnership", "数字经济伙伴关系"]),
    ("RCEP", ["rcep", "regional comprehensive economic partnership"]),
    ("CPTPP", ["cptpp", "comprehensive progressive transpacific partnership"]),
    ("AI_Governance", ["ai governance", "ai safety", "人工智能治理"]),
    ("Cybersecurity", ["cybersecurity", "cyber security", "network security", "网络安全"]),
    ("Privacy_Framework", ["privacy framework", "data privacy framework", "隐私框架"]),
    ("Critical_Infrastructure", ["critical information infrastructure", "ciip", "关键信息基础设施"]),
]

# ============================================================
# 相关度评分
# ============================================================
_RELEVANCE_T1 = [
    "cbpr", "cybersecurity", "data privacy", "ai governance", "ai safety",
    "critical information infrastructure",
    "跨境数据", "网络安全", "人工智能安全", "关键信息基础设施",
]
_RELEVANCE_T2 = [
    "data protection", "cross-border data", "data flow",
    "privacy framework", "ai standard", "ai regulation",
    "ict security", "5g security", "cybercrime",
    "digital sovereignty", "data sovereignty",
    "数据保护", "数据跨境", "AI标准", "5G安全", "数据主权",
]
_RELEVANCE_T3 = [
    "digital trade", "digital economy",
    "connectivity", "infrastructure",
    "trade facilitation", "ftaap",
    "数字贸易", "数字经济", "互联互通",
]
_RELEVANCE_T4 = [
    "joint statement", "ministerial declaration", "communique",
    "联合声明", "部长宣言", "公报", "white paper", "白皮书",
]
_RELEVANCE_TITLE_BONUS = [
    "cbpr", "cybersecurity", "data privacy", "ai governance",
    "critical infrastructure",
    "跨境数据", "网络安全", "人工智能治理", "关键信息基础设施",
]

def classify_article(title, description):
    text = (title + " " + (description or "")).lower()
    cats = []
    for cat, keywords in CORE_MATCH.items():
        for kw in keywords:
            if kw.lower() in text:
                cats.append(cat)
                break
    for kw in CHINA_MATCH:
        if kw.lower() in text:
            cats.append("2026中国年")
            break
    if not cats:
        cats.append("其他APEC动态")
    return list(set(cats))

def extract_doc_type(title, description):
    text = (title + " " + (description or "")).lower()
    types = []
    for dtype, keywords in DOC_TYPE_RULES:
        for kw in keywords:
            if kw.lower() in text:
                types.append(dtype)
                break
    return types if types else ["media_report"]

def extract_apec_bodies(title, description):
    text = (title + " " + (description or "")).lower()
    bodies = []
    for body, keywords in APEC_BODY_RULES:
        for kw in keywords:
            if kw.lower() in text:
                bodies.append(body)
                break
    return bodies

def extract_geo_focus(title, description):
    text = (title + " " + (description or "")).lower()
    geos = []
    for geo, keywords in GEO_RULES:
        for kw in keywords:
            if kw.lower() in text:
                geos.append(geo)
                break
    return geos if geos else ["regional"]

def extract_policy_tags(title, description):
    text = (title + " " + (description or "")).lower()
    tags = []
    for tag, keywords in POLICY_TAG_RULES:
        for kw in keywords:
            if kw.lower() in text:
                tags.append(tag)
                break
    return tags

def calculate_relevance(title, description, categories=None):
    if categories is None:
        categories = []
    title_lower = title.lower()
    desc_lower = description.lower() if description else ""
    text = title_lower + " " + desc_lower
    score = 0
    if "apec" in text or "亚太经合" in title_lower or "亚太经合" in desc_lower:
        score += 20
    elif "asia pacific" in text or "asia-pacific" in text:
        score += 12
    t1_matches = sum(1 for kw in _RELEVANCE_T1 if kw in text)
    score += min(t1_matches * 10, 40)
    t2_matches = sum(1 for kw in _RELEVANCE_T2 if kw in text)
    score += min(t2_matches * 6, 24)
    t3_matches = sum(1 for kw in _RELEVANCE_T3 if kw in text)
    score += min(t3_matches * 2, 8)
    for kw in _RELEVANCE_T4:
        if kw in text:
            score += 8
            break
    for kw in _RELEVANCE_TITLE_BONUS:
        if kw in title_lower:
            score += 8
            break
    score += min(len(categories) * 2, 8)
    if "2026中国年" in categories:
        score += 5
    return min(max(score, 0), 100)

SOURCE_QUALITY_A = {"apec.org", "gov.cn", "mfa.gov.cn", "state.gov",
                    "reuters.com", "ap.org", "apnews.com",
                    "xinhuanet.com", "news.cn", "people.com.cn"}
SOURCE_QUALITY_B = {"bloomberg.com", "ft.com", "wsj.com", "economist.com",
                    "bbc.com", "cnn.com", "nytimes.com", "washingtonpost.com",
                    "scmp.com", "asia.nikkei.com", "straitstimes.com",
                    "csis.org", "cfr.org", "brookings.edu", "oecd.org", "wto.org",
                    "thediplomat.com", "cctv.com", "chinadaily.com.cn",
                    "globaltimes.cn", "chinanews.com"}
SOURCE_QUALITY_C = {"channelnewsasia.com", "thejakartapost.com",
                    "koreaherald.com", "japantimes.co.jp", "bangkokpost.com",
                    "theverge.com", "wired.com", "arstechnica.com",
                    "techcrunch.com", "zdnet.com", "theregister.com",
                    "iapp.org", "cyberscoop.com", "darkreading.com"}
SOURCE_QUALITY_DEFAULT = 4
SOURCE_QUALITY_GREY = 1

def get_source_quality(domain):
    d = domain.lower().replace("www.", "")
    if d in SOURCE_QUALITY_A: return 10
    if d in SOURCE_QUALITY_B: return 8
    if d in SOURCE_QUALITY_C: return 6
    if d in ALLOWED_DOMAINS or any(d.endswith(ad) or ad.endswith(d)
                                    for ad in ALLOWED_DOMAINS if "." in ad):
        return SOURCE_QUALITY_DEFAULT
    return SOURCE_QUALITY_GREY

def enhance_article(article):
    title = article.get("title", "")
    description = article.get("summary", "")
    categories = article.get("categories", [])
    url = article.get("url", "")
    article.setdefault("doc_type", extract_doc_type(title, description))
    article.setdefault("apec_bodies", extract_apec_bodies(title, description))
    article.setdefault("geo_focus", extract_geo_focus(title, description))
    article.setdefault("policy_tags", extract_policy_tags(title, description))
    article.setdefault("relevance", calculate_relevance(title, description, categories))
    article.setdefault("notes", "")
    article.setdefault("starred", False)
    domain = ""
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        pass
    article.setdefault("source_quality", get_source_quality(domain))
    if article["source_quality"] == 1:
        article["relevance"] = max(article["relevance"] - 20, 10)
    return article
