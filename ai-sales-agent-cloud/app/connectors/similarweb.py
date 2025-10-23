import random, pandas as pd
VERT={'SaaS':['acmeapp','cloudify','datapulse','flowhq','marketoid'],'Ecommerce':['shophero','trendify','buybuddy','cartly','dealorama'],'Fintech':['payflux','finastro','bankly','ledgr','coinverse']}
TLD={'DE':'.de','AT':'.at','CH':'.ch','FR':'.fr','US':'.com'}

def search_companies(verticals, countries, min_visits):
    rows=[]
    for v in verticals:
        names=VERT.get(v, VERT['SaaS'])
        for n in names:
            for c in countries:
                t=TLD.get(c,'.com'); visits=random.randint(min_visits, max(min_visits+50000, min_visits*3))
                rows.append({'domain':f"{n}{t}",'company_name':n.capitalize(),'country':c,'vertical':v,'sw_visits':visits})
    df=pd.DataFrame(rows)
    if not df.empty:
        extra=df.sample(min(3,len(df))).copy(); extra['domain']=extra['domain'].str.replace('.com','.io')
        df=pd.concat([df,extra],ignore_index=True)
    return df
