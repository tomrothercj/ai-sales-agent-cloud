# app/connectors/sales_navigator.py
import random
import re
import pandas as pd
from typing import List, Dict

SN_TITLES = [
    "Marketing Manager", "Senior Marketing Manager", "Sales Manager",
    "Account Executive", "BDR", "Head of Partnerships",
    "Head of Marketing", "VP Marketing", "Director Growth",
    "Head of Sales", "VP Sales", "Director Demand Gen"
]
SN_FIRST = ["Chris","Eva","Tom","Julia","Nico","Hannah","Lukas","Marie","Leo","Nina","Clara","Jonas"]
SN_LAST  = ["Schneider","Keller","Hoffmann","Bauer","Brandt","Neumann","Kunz","Zimmer","Becker","Wagner","Fischer","Schmidt"]

def _person_slug(first: str, last: str, domain: str) -> str:
    # Create a deterministic, person-like slug so it visibly looks like a LinkedIn profile URL
    suffix = abs(hash(f"{domain}|{first}|{last}")) % 100000
    return f"{first.lower()}-{last.lower()}-{suffix}"

def find_personas_from_account_list(company_domains: List[str], titles_regex: str) -> pd.DataFrame:
    """
    Mock Sales Navigator:
      - Generate 1..3 leads per company
      - Filter by titles_regex (case-insensitive)
      - Email stays blank; LinkedIn profile is a person-style URL (/in/slug/)
    """
    try:
        pattern = re.compile(titles_regex or "", re.IGNORECASE)
    except re.error:
        pattern = re.compile(".*")  # match all if regex invalid

    rows: List[Dict] = []
    for domain in company_domains:
        # Generate a few leads to increase chance of regex matches
        for _ in range(random.choice([1, 2, 3])):
            fn = random.choice(SN_FIRST)
            ln = random.choice(SN_LAST)
            title = random.choice(SN_TITLES)
            if not pattern.search(title or ""):
                continue
            slug = _person_slug(fn, ln, domain)
            rows.append({
                "company_domain": domain,
                "full_name": f"{fn} {ln}",
                "title": title,
                "email": "",  # per requirement: keep empty for Sales Navigator
                "li_profile": f"https://www.linkedin.com/in/{slug}/",
                "source": "sales_navigator",
                "confidence": 0.6
            })
    return pd.DataFrame(rows)
