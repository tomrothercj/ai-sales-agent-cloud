import random, pandas as pd
TIT=['VP Marketing','Head of Marketing','Director Demand Gen','VP Sales','Head of Sales','Director Growth']

def enrich_company(domain):
    if random.random()<0.8:
        return {'id':f"ZC_{abs(hash(domain))%10000}",'linkedin_url':f"https://www.linkedin.com/company/{domain.split('.')[0]}/"}
    return None

def find_personas(zoom_id, titles_regex, country):
    n=random.choice([0,1,2,3]); rows=[]
    for _ in range(n):
        nm=random.choice(['Jane','John','Max','Mia','Alex','Lena','Sara','Paul']); ln=random.choice(['Muster','Doe','Klein','Weber','Fischer','Schmidt'])
        title=random.choice(TIT)
        rows.append({'company_domain':'unknown','full_name':f'{nm} {ln}','title':title,'email':None,'li_profile':f"https://www.linkedin.com/in/{nm.lower()}{ln.lower()}",'source':'zoominfo','confidence':round(random.uniform(0.6,0.95),2)})
    return pd.DataFrame(rows)
