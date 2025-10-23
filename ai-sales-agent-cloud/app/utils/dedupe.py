# app/utils/dedupe.py
from difflib import SequenceMatcher
import pandas as pd

def canonical_domain(domain: str) -> str:
    domain = (domain or '').lower().strip()
    if domain.startswith('http'):
        domain = domain.split('://', 1)[1]
    return domain.strip('/')

def simple_company_name_from_domain(domain: str) -> str:
    base = canonical_domain(domain).split('.')[0]
    return base.capitalize()

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['domain'] = df['domain'].apply(canonical_domain)
    if 'company_name' not in df.columns or df['company_name'].isna().all():
        df['company_name'] = df['domain'].apply(simple_company_name_from_domain)
    return df

def _sim(a: str, b: str) -> float:
    # SequenceMatcher returns [0..1]
    return SequenceMatcher(None, (a or ''), (b or '')).ratio()

def fuzzy_dedupe(df: pd.DataFrame, threshold: float = 0.92) -> pd.DataFrame:
    """
    Drops near-duplicates by company_name within the same country.
    Uses difflib ratio (stdlib) instead of rapidfuzz.
    """
    df = df.drop_duplicates(subset=['domain']).reset_index(drop=True)
    keep_idx = []
    seen = set()
    for i, row in df.iterrows():
        if i in seen:
            continue
        keep_idx.append(i)
        name_i = row.get('company_name', '') or ''
        for j in range(i + 1, len(df)):
            if j in seen:
                continue
            # only compare inside the same country
            if row.get('country') != df.at[j, 'country']:
                continue
            name_j = df.at[j, 'company_name'] or ''
            if _sim(name_i, name_j) >= threshold:
                seen.add(j)
    return df.loc[keep_idx].reset_index(drop=True)
