# app/utils/sales_navigator_csv.py
import os
import pandas as pd

REQUIRED_COLUMNS = ['Company Name','Company Website','Company LinkedIn URL','Country']

def accounts_csv(companies_df: pd.DataFrame, path: str):
    # ensure parent directory exists
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    rows = []
    for _, c in companies_df.iterrows():
        rows.append({
            'Company Name': c.get('company_name') or c['domain'],
            'Company Website': c.get('company_url') or f"https://{c['domain']}",   # prefer company_url if present
            'Company LinkedIn URL': c.get('li_company_url') or '',
            'Country': c.get('hq_country') or c.get('country') or ''               # prefer HQ country
        })
    pd.DataFrame(rows, columns=REQUIRED_COLUMNS).to_csv(path, index=False)
    return path
