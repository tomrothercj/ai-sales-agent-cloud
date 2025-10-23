import pandas as pd
REQUIRED=['Company Name','Company Website','Company LinkedIn URL','Country']

def accounts_csv(df:pd.DataFrame, path:str):
    rows=[{'Company Name':r.get('company_name') or r['domain'],
           'Company Website':f"https://{r['domain']}",
           'Company LinkedIn URL':r.get('li_company_url') or '',
           'Country':r.get('country') or ''} for _,r in df.iterrows()]
    pd.DataFrame(rows, columns=REQUIRED).to_csv(path, index=False)
    return path
