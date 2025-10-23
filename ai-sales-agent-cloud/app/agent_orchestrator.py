from typing import Dict, Tuple
import pandas as pd
from app.connectors import similarweb as sw
from app.connectors import zoominfo as zi
from app.connectors import salesforce as sf
from app.utils.dedupe import normalize, fuzzy_dedupe
from app.utils.sales_navigator_csv import accounts_csv

def run_pipeline(params:Dict, ui_decisions:Dict)->Tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame]:
    if params.get('mini_mode'):
        import random
        random.seed(42)
        try:
            import numpy as np
            np.random.seed(42)
        except Exception:
            pass
    raw=sw.search_companies(params['verticals'], params['countries'], params['min_monthly_visits'])
    norm=normalize(raw); deduped=fuzzy_dedupe(norm, 92)
    if params.get('mini_mode'): deduped=deduped.head(5).reset_index(drop=True)
    if ui_decisions.get('keep_domains'):
        extra=norm[norm['domain'].isin(ui_decisions['keep_domains'])]
        deduped=pd.concat([deduped,extra]).drop_duplicates(subset=['domain']).reset_index(drop=True)
    deduped['sf_account_id']=deduped['domain'].apply(sf.find_account_by_domain)
    for d in ui_decisions.get('create_sf_accounts', []):
        idx=deduped.index[deduped['domain']==d]
        if len(idx): deduped.loc[idx,'sf_account_id']=sf.create_account(deduped.loc[idx[0],'company_name'], d)
    enriched=[]; leads_all=[]
    for _,row in deduped.iterrows():
        z=zi.enrich_company(row['domain']); li=z.get('linkedin_url') if z else None; zid=z.get('id') if z else None
        ppl=zi.find_personas(zid, params['titles_regex'], row.get('country')) if zid else pd.DataFrame()
        if not ppl.empty:
            ppl['company_domain']=row['domain']; leads_all.append(ppl)
        enriched.append({**row.to_dict(),'zoominfo_company_id':zid,'li_company_url':li})
    companies=pd.DataFrame(enriched)
    leads=pd.concat(leads_all) if leads_all else pd.DataFrame(columns=['company_domain','full_name','title','email','li_profile','source','confidence'])
    needs=companies[~companies['domain'].isin(leads['company_domain'])]
    accounts_csv(needs, 'data/outputs/sn_accounts_upload.csv')
    with pd.ExcelWriter('data/outputs/final.xlsx') as xl:
        companies.to_excel(xl, 'Companies', index=False)
        leads.to_excel(xl, 'Leads', index=False)
        needs.to_excel(xl, 'Needs_SalesNav', index=False)
    return companies, leads, needs
