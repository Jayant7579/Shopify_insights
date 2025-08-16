import json
import time
from typing import List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
from .utils import DEFAULT_HEADERS, normalize_url, absolutize, EMAIL_RE, PHONE_RE
from .models import BrandResponse, Product, FAQ, ContactDetails, PolicyLink

TIMEOUT = 20
SESSION = requests.Session()
SESSION.headers.update(DEFAULT_HEADERS)

def get(url: str):
    r = SESSION.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    return r

def is_shopify_like(base_url: str, home_html: str) -> bool:
    try:
        pj = SESSION.get(f"{base_url}/products.json?limit=1", timeout=TIMEOUT)
        if pj.status_code == 200 and pj.headers.get("content-type","").startswith("application/json"):
            j = pj.json()
            if isinstance(j, dict) and "products" in j:
                return True
    except Exception:
        pass
    soup = BeautifulSoup(home_html, "lxml")
    scripts = " ".join([s.get("src","") for s in soup.find_all("script") if s.get("src")])
    metas = " ".join([m.get("content","") for m in soup.find_all("meta") if m.get("content")])
    return ("shopify" in scripts.lower()) or ("shopify" in metas.lower())

def fetch_products(base_url: str, limit: int = 250, max_pages: int = 10) -> List[Product]:
    products: List[Product] = []
    for page in range(1, max_pages + 1):
        url = f"{base_url}/products.json?limit={limit}&page={page}"
        try:
            r = get(url)
            if r.status_code != 200:
                break
            data = r.json()
            batch = data.get("products", []) if isinstance(data, dict) else []
            if not batch:
                break
            for p in batch:
                handle = p.get("handle")
                products.append(Product(
                    id=p.get("id"),
                    title=p.get("title"),
                    handle=handle,
                    body_html=p.get("body_html"),
                    vendor=p.get("vendor"),
                    product_type=p.get("product_type"),
                    tags=p.get("tags"),
                    url=f"{base_url}/products/{handle}" if handle else None
                ))
        except Exception:
            break
    seen = set()
    unique = []
    for p in products:
        key = p.id or p.handle or p.title
        if key and key not in seen:
            seen.add(key)
            unique.append(p)
    return unique

def extract_hero_products(base_url: str, home_html: str) -> List[Product]:
    soup = BeautifulSoup(home_html, "lxml")
    links = soup.select("a[href*='/products/']")
    seen = set()
    heroes: List[Product] = []
    for a in links[:30]:
        href = a.get("href", "")
        full = absolutize(base_url, href)
        if "/products/" not in full or full in seen:
            continue
        seen.add(full)
        title = a.get_text(strip=True)
        handle = full.split("/products/")[-1].strip("/").split("?")[0]
        heroes.append(Product(title=title or handle, handle=handle, url=full))
    return heroes

def find_policy_link(base_url: str, home_html: str, keywords: List[str]) -> Optional[PolicyLink]:
    soup = BeautifulSoup(home_html, "lxml")
    for a in soup.find_all("a", href=True):
        h = a["href"].lower()
        if any(k in h for k in keywords):
            url = absolutize(base_url, a["href"])
            try:
                html = get(url).text
                excerpt = BeautifulSoup(html, "lxml").get_text(" ", strip=True)[:600]
            except Exception:
                excerpt = None
            return PolicyLink(title=a.get_text(strip=True) or keywords[0].title(), url=url, text_excerpt=excerpt)
    return None

def extract_socials_and_links(base_url: str, home_html: str) -> Tuple[List[str], List[str]]:
    soup = BeautifulSoup(home_html, "lxml")
    socials = []
    important = set()
    social_domains = ["facebook.com", "instagram.com", "tiktok.com", "twitter.com", "x.com", "youtube.com", "pinterest.com", "linkedin.com"]
    important_keys = ["contact", "blog", "order", "track", "tracking", "help", "support", "faq", "shipping", "warranty", "care"]
    for a in soup.find_all("a", href=True):
        href = absolutize(base_url, a["href"])
        low = href.lower()
        if any(dom in low for dom in social_domains):
            socials.append(href)
        if any(k in low for k in important_keys):
            important.add(href)
    return list(dict.fromkeys(socials)), sorted(important)

def extract_contact_details(base_url: str, home_html: str) -> ContactDetails:
    soup = BeautifulSoup(home_html, "lxml")
    emails = set()
    phones = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("mailto:"):
            emails.add(href.replace("mailto:", "").strip())
        if href.startswith("tel:"):
            phones.add(href.replace("tel:", "").strip())
    text = soup.get_text(" ", strip=True)
    emails.update(EMAIL_RE.findall(text))
    phones.update([p for p in PHONE_RE.findall(text) if len(p) >= 7])
    return ContactDetails(emails=sorted(emails), phones=sorted(phones), addresses=[])

def extract_about(base_url: str, home_html: str) -> Optional[str]:
    soup = BeautifulSoup(home_html, "lxml")
    md = soup.find("meta", attrs={"name": "description"})
    if md and md.get("content"):
        return md["content"].strip()
    og = soup.find("meta", attrs={"property": "og:description"})
    if og and og.get("content"):
        return og["content"].strip()
    for a in soup.find_all("a", href=True):
        if "about" in a["href"].lower():
            url = absolutize(base_url, a["href"])
            try:
                html = get(url).text
                t = BeautifulSoup(html, "lxml").get_text(" ", strip=True)
                return t[:600]
            except Exception:
                continue
    return None

def extract_faqs(base_url: str, home_html: str) -> List[FAQ]:
    faqs: List[FAQ] = []
    soup = BeautifulSoup(home_html, "lxml")
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "{}")
        except Exception:
            continue
        blocks = data if isinstance(data, list) else [data]
        for d in blocks:
            if isinstance(d, dict) and str(d.get("@type","")).lower() == "faqpage":
                for q in d.get("mainEntity", []) or d.get("mainEntityOfPage", []):
                    if isinstance(q, dict):
                        question = q.get("name") or q.get("question") or ""
                        ans = ""
                        accepted = q.get("acceptedAnswer") or {}
                        if isinstance(accepted, dict):
                            ans = accepted.get("text") or ""
                        if question and ans:
                            from bs4 import BeautifulSoup as BS2
                            faqs.append(FAQ(question=question.strip(), answer=BS2(ans, "lxml").get_text(" ", strip=True)))
    if not faqs:
        for a in soup.find_all("a", href=True):
            if any(k in a["href"].lower() for k in ["faq", "help", "support"]):
                url = absolutize(base_url, a["href"])
                try:
                    html = get(url).text
                    faqs.extend(parse_faq_from_page(html))
                    if faqs:
                        break
                except Exception:
                    continue
    return faqs[:50]

def parse_faq_from_page(html: str) -> List[FAQ]:
    soup = BeautifulSoup(html, "lxml")
    faqs: List[FAQ] = []
    for h in soup.select("h1,h2,h3,h4"):
        q = h.get_text(" ", strip=True)
        if not q or len(q) < 5:
            continue
        sib = h.find_next_sibling()
        answer_chunks = []
        steps = 0
        while sib and steps < 5 and sib.name not in ["h1","h2","h3","h4"]:
            answer_chunks.append(sib.get_text(" ", strip=True))
            sib = sib.find_next_sibling()
            steps += 1
        ans = " ".join([c for c in answer_chunks if c]).strip()
        if q and ans:
            faqs.append(FAQ(question=q, answer=ans[:800]))
    return faqs

def fetch_brand_data(website_url: str) -> BrandResponse:
    base = normalize_url(website_url)
    try:
        home_html = get(base).text
    except Exception as e:
        return BrandResponse(website_url=base, errors=[f"Home fetch failed: {e}"])

    shopify_like = is_shopify_like(base, home_html)
    products = fetch_products(base) if shopify_like else []
    heroes = extract_hero_products(base, home_html)
    privacy = find_policy_link(base, home_html, ["privacy"])
    returns = find_policy_link(base, home_html, ["return", "refund"])
    socials, important_links = extract_socials_and_links(base, home_html)
    contact = extract_contact_details(base, home_html)
    about = extract_about(base, home_html)
    faqs = extract_faqs(base, home_html)

    return BrandResponse(
        website_url=base,
        is_shopify_like=shopify_like,
        product_catalog=products,
        hero_products=heroes,
        privacy_policy=privacy,
        return_refund_policy=returns,
        faqs=faqs,
        social_handles=socials,
        contact_details=contact,
        about_brand=about,
        important_links=important_links,
        fetched_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        errors=[]
    )
