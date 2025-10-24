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

def find_personas_from_account_list(company_domains: List[str], titles_regex: str) -> pd.DataFrame:
    """
    Mock Sales Navigator:
      - Generate 0..2 leads per company
      - Filter by titles_regex (case-insensitive)
      - Email stays blank by design; LinkedIn profile is provided
    """
    try:
        pattern = re.compile(titles_regex or "", re.IGNORECASE)
    except re.error:
        # Fallback: if regex is invalid, treat as match-all
        pattern = re.compile(".*")

    rows: List[Dict] = []
    for domain in company_domains:
        n = random.choice([0, 1, 2])
        for _ in range(n):
            fn = random.choice(SN_FIRST)
            ln = random.choice(SN_LAST)
            title = random.choice(SN_TITLES)
            if not pattern.search(title or ""):
                continue
            rows.append({
                "company_domain": domain,
                "full_name": f"{fn} {ln}",
                "title": title,
                "email": "",  # keep empty for Sales Navigator
                "li_profile": f"https://www.linkedin.com/in/{fn.lower()}{ln.lower()}",
                "source": "sales_navigator",
                "confidence": 0.6
            })
    return pd.DataFrame(rows)
