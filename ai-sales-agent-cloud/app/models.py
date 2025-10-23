from dataclasses import dataclass
from typing import Optional
@dataclass
class Company:
    domain:str
    company_name:Optional[str]=None
    country:Optional[str]=None
    vertical:Optional[str]=None
    sw_visits:Optional[int]=None
    sf_account_id:Optional[str]=None
    zoominfo_company_id:Optional[str]=None
    li_company_url:Optional[str]=None
    status:str='pending'
@dataclass
class Lead:
    company_domain:str
    full_name:str
    title:str
    email:Optional[str]
    li_profile:Optional[str]
    source:str
    confidence:float
