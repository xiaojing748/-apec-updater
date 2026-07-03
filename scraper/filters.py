"""Article filters - v3: aligned with project requirements (APEC x cybersecurity)"""
import re
from urllib.parse import urlparse
from scraper import config

def deduplicate(articles):
    seen = set()
    unique = []
    for a in articles:
        url = a.get("url", "").strip().lower().rstrip("/")
        if url and url not in seen:
            seen.add(url)
            unique.append(a)
    unique = _title_dedup(unique)
    return unique

def _tokenize(s):
    s = s.lower()
    s = re.sub(r"[^\w\s\u4e00-\u9fff]", " ", s)
    tokens = s.split()
    bigrams = set()
    for i in range(len(tokens) - 1):
        bigrams.add(tokens[i] + " " + tokens[i + 1])
    for t in tokens:
        if len(t) >= 3:
            bigrams.add(t)
    return bigrams

def _title_dedup(articles, threshold=0.65):
    result = []
    for a in articles:
        title_a = _tokenize(a.get("title", ""))
        if not title_a:
            result.append(a)
            continue
        is_dup = False
        for b in result:
            title_b = _tokenize(b.get("title", ""))
            if not title_b:
                continue
            intersection = len(title_a & title_b)
            union = len(title_a | title_b)
            if union > 0 and (intersection / union) >= threshold:
                if len(a.get("summary", "")) > len(b.get("summary", "")):
                    result[result.index(b)] = a
                is_dup = True
                break
        if not is_dup:
            result.append(a)
    return result

def filter_by_domain(articles):
    result = []
    for a in articles:
        domain = _extract_domain(a.get("url", ""))
        if not domain:
            continue
        if domain in config.BLOCKED_DOMAINS or any(
            domain.endswith(d) for d in config.BLOCKED_DOMAINS
        ):
            continue
        result.append(a)
    return result

# ---- APEC context identifiers ----
_APEC_BODY_ABBRS = [
    "abac", "telwg", "desg", "ecsg", "som", "mrt", "cti", "telmin",
    "dps", "dpsg", "cisg", "apmen", "hod",
]
_APEC_BODY_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(a) for a in _APEC_BODY_ABBRS) + r")\b",
    re.IGNORECASE
)

# ---- STRONG_KW: cybersecurity core (project-mandated) ----
# Match 1 = accepted even without APEC context
STRONG_KW = [
    # APEC identifiers
    "apec", "亚太经合",
    # Data privacy
    "cbpr", "cross-border privacy", "cross border privacy",
    "data privacy", "data protection", "data sovereignty",
    "data localization", "data localisation",
    "cross-border data", "cross border data",
    "data free flow with trust", "privacy framework", "privacy shield",
    "personal data", "personal information",
    "跨境数据", "数据跨境", "数据隐私", "数据保护",
    "数据主权", "数据本地化", "数据出境",
    "个人信息", "隐私框架", "隐私保护",
    # AI governance
    "ai governance", "ai safety", "ai ethics",
    "artificial intelligence governance",
    "ai regulation", "ai standard",
    "人工智能治理", "人工智能安全", "人工智能标准",
    "responsible ai",
    # Cybersecurity core
    "cybersecurity", "cyber security", "cybercrime", "cyber crime",
    "网络安全", "网络犯罪", "网络攻击",
    "critical information infrastructure", "关键信息基础设施",
    "ciip", "关基保护",
    "5g security", "5g安全", "ict security",
    "cloud security", "data breach",
    "cert", "csirt",
    "telecom security", "telecommunications security",
    "电信安全", "通信安全",
    # Geo-security
    "digital sovereignty", "tech decoupling",
    "cyber deterrence", "cyber norms",
    "数字主权", "科技脱钩",
]

# ---- LOOSE_KW: economic/political context (needs APEC context) ----
LOOSE_KW = [
    # Digital economy (security context needed)
    "digital trade", "digital economy",
    "数字贸易", "数字经济",
    "digital governance", "digital services regulation",
    "数字治理",
    # Connectivity / infrastructure (security context needed)
    "connectivity", "互联互通",
    "digital infrastructure",
    "5g network", "telecom standard", "telecom infrastructure",
    # Geo-economic
    "ftaap", "multilateral security", "security governance",
    "economic security", "economic coercion",
    "安全治理", "经济安全",
    # China year
    "som1", "som2", "som3", "中国年", "host year",
]

def _has_apec_context(text):
    if "apec" in text or "亚太经合" in text:
        return True
    return bool(_APEC_BODY_RE.search(text))

def _has_apec_body_in_title(title):
    return bool(_APEC_BODY_RE.search(title))

def _count_kw_matches(text, kw_list):
    count = 0
    for kw in kw_list:
        if kw.lower() in text:
            count += 1
    return count

def filter_by_keywords(articles):
    """APEC context → pass; otherwise need STRONG_KW match"""
    result = []
    for a in articles:
        text = (a.get("title", "") + " " + a.get("summary", "")).lower()
        if _has_apec_context(text):
            result.append(a)
        elif _count_kw_matches(text, STRONG_KW) >= 1:
            result.append(a)
    return result

# ---- Negative keywords ----
NEGATIVE_KW = [
    "妇联", "妇女运动", "妇女权益", "妇女发展",
    "女企业家", "女性创业", "女性发展", "women entrepreneur",
    "女足", "女排",
    "足球赛", "篮球赛", "奥运", "世界杯", "欧冠",
    "娱乐圈", "综艺", "明星", "演唱会",
    "村委会", "街道办", "社区治理",
    "抗癌", "肿瘤", "手术", "疫苗研发", "新药",
    "高考", "中考", "考研", "留学",
    "养殖", "种植", "农产品", "粮食",
]

NEGATIVE_OVERRIDE_KW = [
    "cybersecurity", "cyber security", "data privacy", "data protection",
    "网络安全", "数据隐私", "数据保护", "数据安全",
    "数据跨境", "ai governance", "人工智能治理",
    "critical information", "关键信息",
    "cbpr", "telwg", "desg", "ecsg",
]

def filter_by_quality(articles):
    result = []
    for a in articles:
        title = a.get("title", "").strip()
        summary = a.get("summary", "").strip()
        text = (title + " " + summary).lower()

        if len(title) < 10 and not _has_apec_body_in_title(title):
            continue
        if len(summary) < 20 and not _has_apec_context(title.lower()):
            continue

        # Negative keyword check
        neg_hits = [kw for kw in NEGATIVE_KW if kw.lower() in text]
        if neg_hits:
            has_override = any(kw.lower() in text for kw in NEGATIVE_OVERRIDE_KW)
            if not has_override:
                continue

        # Skip patterns
        skip_patterns = [
            r"^latest news$", r"^breaking news$", r"^trending$",
            r"^top stories$", r"^news headlines$", r"^today.*news$",
            r"^news archive$", r"^search results", r"^page not found",
            r"^404", r"^access denied", r"^subscribe",
        ]
        if any(re.search(p, title, re.IGNORECASE) for p in skip_patterns):
            continue

        # Ad patterns
        ad_patterns = [
            r"subscribe\s*(now|today|for free)", r"sign up\s*(now|today|here)",
            r"click here\s*(to|for)", r"\badvertisement\b", r"\bsponsored\b",
        ]
        if any(re.search(p, summary, re.IGNORECASE) for p in ad_patterns):
            continue

        result.append(a)
    return result

def enhance_metadata(articles):
    return [config.enhance_article(a) for a in articles]

def apply(articles):
    url_valid = [a for a in articles if _is_valid_url(a.get("url", ""))]
    unique = deduplicate(url_valid)
    domain_filtered = filter_by_domain(unique)
    keyword_filtered = filter_by_keywords(domain_filtered)
    quality_filtered = filter_by_quality(keyword_filtered)
    enhanced = enhance_metadata(quality_filtered)
    return enhanced

def _extract_domain(url):
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""

_SEARCH_DOMAINS = {"bing.com", "google.com", "search.yahoo.com", "baidu.com"}

def _is_valid_url(url):
    if not url:
        return False
    lower = url.lower()
    if "/search" in lower:
        return False
    domain = _extract_domain(url)
    if domain in _SEARCH_DOMAINS:
        return False
    return True
