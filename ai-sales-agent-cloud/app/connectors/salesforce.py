import random

def find_account_by_domain(domain):
    return f"001{abs(hash(domain))%1000000:06d}" if random.random()<0.5 else None

def create_account(company_name, domain):
    return f"001NEW{abs(hash(domain))%1000:03d}"
