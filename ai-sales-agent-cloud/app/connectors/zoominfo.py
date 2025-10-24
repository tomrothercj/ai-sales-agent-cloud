# app/connectors/zoominfo.py
import random
import re
import pandas as pd
from typing import Dict, List, Optional

TITLES = [
    'VP Marketing','Head of Marketing','Director Demand Gen',
    'VP Sales','Head of Sales','Director Growth'
]

TRANSLIT = str.maketrans({
    "ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss"
})

def _clean(s: str) -> str:
    s = (s or "").strip().translate(TRANSLIT)
    s = re.sub(r"[^a-zA-Z\- ]", "", s)
    return s

def _email_for(first: str, last: str, domain: str) -> str:
    """Deterministic common patterns to simulate ZoomInfo-provided emails."""
    f = _clean(first).lower().replace(" ", "")
    l = _clean(last).lower().replace(" ", "")
    base = f"{domain}|{f}|{l}"
    idx = abs(hash(base)) % 5
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
    local = local.strip(".-_")
    return f"{local}@{domain}"

def enrich_company(domain: str) -> Optional[Dict]:
    if random.random() < 0.8:
        return {
            'id': f'ZC_{abs(hash(domain)) % 10_000}',
            'linkedin_url': f'https://www.linkedin.com/company/{domain.split(".")[0]}/'
        }
    return None

def find_personas(
    zoominfo_company_id: str,
    titles_regex: str,
    country: Optional[str],
    company_domain: str,
    enable_email_enrichment: bool = True
) -> pd.DataFrame:
    """
    Mock ZoomInfo: return 0..3 personas. If enable_email_enrichment=False, email field is left blank.
    """
    n = random.choice([0, 1, 2, 3])
    rows: List[Dict] = []
    first_names = ['Jane','John','Max','Mia','Alex','Lena','Sara','Paul']
    last_names  = ['Muster','Doe','Klein','Weber','Fischer','Schmidt','Wagner','Becker']

    for _ in range(n):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        title = random.choice(TITLES)
        email = _email_for(fn, ln, company_domain) if enable_email_enrichment else ""

        rows.append({
            'company_domain': company_domain,
            'full_name': f'{fn} {ln}',
            'title': title,
            'email': email,  # filled or blank based on toggle
         slug = f"{fn.lower()}-{ln.lower()}-{abs(hash(company_domain + fn + ln)) % 100000}"
'li_profile': f'https://www.linkedin.com/in/{slug}/',
            'source': 'zoominfo',
            'confidence': round(random.uniform(0.6, 0.95), 2)
        })

    return pd.DataFrame(rows)
