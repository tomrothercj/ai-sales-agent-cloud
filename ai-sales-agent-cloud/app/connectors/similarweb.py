# app/connectors/similarweb.py
import random
import pandas as pd
from typing import List, Dict

VERTICAL_SAMPLES = {
    'SaaS': ['acmeapp','cloudify','datapulse','flowhq','marketoid'],
    'Ecommerce': ['shophero','trendify','buybuddy','cartly','dealorama'],
    'Fintech': ['payflux','finastro','bankly','ledgr','coinverse']
}

COUNTRY_DOMAINS = {'DE':'.de','AT':'.at','CH':'.ch','FR':'.fr','US':'.com'}

def search_companies(verticals: List[str], countries: List[str], min_visits: int) -> pd.DataFrame:
    rows: List[Dict] = []
    for v in verticals:
        names = VERTICAL_SAMPLES.get(v, VERTICAL_SAMPLES['SaaS'])
        for name in names:
            for c in countries:
                tld = COUNTRY_DOMAINS.get(c, '.com')
                visits = random.randint(min_visits, max(min_visits + 50_000, min_visits * 3))

                # Mock HQ logic:
                # - 70%: HQ in the same country as the result row
                # - 30%: HQ in a random of the selected countries (or fallback to the same)
                if countries:
                    hq = c if random.random() < 0.7 else random.choice(countries)
                else:
                    hq = c

                domain = f"{name}{tld}"
                rows.append({
                    'domain': domain,
                    'company_name': name.capitalize(),
                    'country': c,           # result row country / market
                    'hq_country': hq,       # NEW: headquarters country
                    'vertical': v,
                    'sw_visits': visits,
                    'company_url': f"https://{domain}"  # NEW: canonical company URL
                })

    df = pd.DataFrame(rows)

    # Add a few domain variants (for dedupe demo)
    if not df.empty:
        extra = df.sample(min(3, len(df))).copy()
        extra['domain'] = extra['domain'].str.replace('.com', '.io', regex=False)
        # keep same metadata for the variant rows
        df = pd.concat([df, extra], ignore_index=True)

    return df
