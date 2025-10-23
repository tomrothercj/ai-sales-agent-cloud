from rapidfuzz import fuzz
import pandas as pd

def canonical_domain(d:str)->str:
    d=(d or '').lower().strip()
    if d.startswith('http'): d=d.split('://',1)[1]
    return d.strip('/')

def simple_company_name_from_domain(d:str)->str:
    return canonical_domain(d).split('.')[0].capitalize()

def normalize(df:pd.DataFrame)->pd.DataFrame:
    df=df.copy(); df['domain']=df['domain'].apply(canonical_domain)
    if 'company_name' not in df.columns or df['company_name'].isna().all():
        df['company_name']=df['domain'].apply(simple_company_name_from_domain)
    return df

def fuzzy_dedupe(df:pd.DataFrame, threshold:int=92)->pd.DataFrame:
    df=df.drop_duplicates(subset=['domain']).reset_index(drop=True)
    keep,seen=[],set()
    for i,row in df.iterrows():
        if i in seen: continue
        keep.append(i)
        n1=row.get('company_name','') or ''
        for j in range(i+1,len(df)):
            if j in seen: continue
            if row.get('country')!=df.at[j,'country']: continue
            n2=df.at[j,'company_name'] or ''
            if fuzz.WRatio(n1,n2)>=threshold: seen.add(j)
    return df.loc[keep].reset_index(drop=True)
