# app/connectors/sales_navigator.py
import random
import pandas as pd
from typing import List, Dict

SN_TITLES = [
    "Marketing Manager", "Senior Marketing Manager", "Sales Manager",
    "Account Executive", "BDR", "Head of Partnerships"
]
SN_FIRST = ["Chris","Eva","Tom","Julia","Nico","Hannah","Lukas","Marie"]
SN_LAST  = ["Schneider","Keller","Hoffmann","Bauer","Brandt","Neumann","Kunz","Zimmer"]

def find_personas_from_account_list(company_domains: List[str]) -> pd.DataFrame:
    """
    Mock Sales Navigator: return 0..2 leads per company.
    Emails are intentionally blank; LinkedIn profile is provided.
    """
    rows: List[Dict] = []
    for domain in company_domains:
        n = random.choice([0, 1, 2])
        for _ in range(n):
            fn = random.choice(SN_FIRST)
            ln = random.choice(SN_LAST)
            rows.append({
                "company_domain": domain,
                "full_name": f"{fn} {ln}",
                "title": random.choice(SN_TITLES),
                "email": "",  # per requirement: keep empty for Sales Navigator
                "li_profile": f"https://www.linkedin.com/in/{fn.lower()}{ln.lower()}",
                "source": "sales_navigator",
                "confidence": 0.6
            })
    return pd.DataFrame(rows)
