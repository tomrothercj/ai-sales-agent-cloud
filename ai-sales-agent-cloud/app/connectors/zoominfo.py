# app/connectors/zoominfo.py
import random
import re
import pandas as pd
from typing import Dict, List, Optional

TITLES = [
    "VP Marketing", "Head of Marketing", "Director Demand Gen",
    "VP Sales", "Head of Sales", "Director Growth"
]

def _clean(s: str) -> str:
    """Basic sanitizer: keep letters and dashes/spaces, strip others."""
    s = (s or "").strip()
    return re.sub(r"[^a-zA-Z\- ]", "", s)

def _email_for(first: str, last: str, domain: str) -> str:
    """
    Deterministically generate a plausible business email using common patterns.
    Patterns:
      0: first.last@domain
      1: f.last@domain
      2: first.l@domain
      3: first@domain
      4: first_last@domain
    """
    f = _clean(first).lower().replace(" ", "")
    l = _clean(last).lower().replace(" ", "")
    idx = abs(hash(f"{domain}|{f}|{l}")) % 5

    if idx == 0:
        local = f"{f}.{l}"
    elif idx == 1:
        local = f"{f[:1]}.{l}"
    elif idx == 2:
        local = f"{f}.{l[:1]}"
    elif idx == 3:
        local = f"{f}"
    else:
        local = f"{f}_{l}"

    local = local.strip(".-_") or f  # guard against empty local part
    return f"{local}@{domain}"

def _person_slug(first: str, last: str, domain: str) -> str:
    """Create a deterministic person-like slug for a LinkedIn profile URL."""
    suffix = abs(hash(f"{domain}|{first}|{last}")) % 100000
    return f"{first.lower()}-{last.lower()}-{suffix}"

def enrich_company(domain: str) -> Optional[Dict]:
    """Mock: 80% of domains have a ZoomInfo company with a company LinkedIn URL."""
    if random.random() < 0.8:
        company = domain.split(".")[0]
        return {
            "id": f"ZC_{abs(hash(domain)) % 10000}",
            "linkedin_url": f"https://www.linkedin.com/company/{company}/",
        }
    return None

def find_personas(
    zoominfo_company_id: str,
    titles_regex: str,
    country: Optional[str],
    company_domain: str,
    enable_email_enrichment: bool = True,
) -> pd.DataFrame:
    """
    Mock ZoomInfo: return 0..3 personas.
    - Email is populated if enable_email_enrichment=True, else left blank.
    - li_profile uses a person-style LinkedIn URL (/in/<slug>/).
    """
    # compile regex safely
    try:
        pattern = re.compile(titles_regex or "", re.IGNORECASE)
    except re.error:
        pattern = re.compile(".*")  # match-all on invalid regex

    n = random.choice([0, 1, 2, 3])
    rows: List[Dict] = []

    first_names = ["Jane", "John", "Max", "Mia", "Alex", "Lena", "Sara", "Paul"]
    last_names = ["Muster", "Doe", "Klein", "Weber", "Fischer", "Schmidt", "Wagner", "Becker"]

    for _ in range(n):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        title = random.choice(TITLES)

        # respect titles regex
        if not pattern.search(title or ""):
            continue

        email = _email_for(fn, ln, company_domain) if enable_email_enrichment else ""
        slug = _person_slug(fn, ln, company_domain)

        rows.append({
            "company_domain": company_domain,
            "full_name": f"{fn} {ln}",
            "title": title,
            "email": email,
            "li_profile": f"https://www.linkedin.com/in/{slug}/",
            "source": "zoominfo",
            "confidence": round(random.uniform(0.6, 0.95), 2),
        })

    return pd.DataFrame(rows)
