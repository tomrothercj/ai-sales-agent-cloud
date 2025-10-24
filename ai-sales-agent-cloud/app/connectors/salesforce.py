# app/connectors/salesforce.py
import random
from typing import Optional

__all__ = ["find_account_by_domain", "create_account"]

def find_account_by_domain(domain: str) -> Optional[str]:
    """
    Mock: ~50% of companies already exist in Salesforce.
    Returns an Account ID string or None.
    """
    if not isinstance(domain, str) or not domain:
        return None
    if random.random() < 0.5:
        return f"001{abs(hash(domain)) % 1_000_000:06d}"
    return None

def create_account(company_name: str, domain: str) -> str:
    """
    Mock: create and return a new Account ID.
    """
    base = (domain or company_name or "new").strip().lower()
    return f"001NEW{abs(hash(base)) % 1_000:03d}"
