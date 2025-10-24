# app/agent_orchestrator.py
from typing import Dict, Tuple
import os
import pandas as pd

from app.connectors import similarweb as sw
from app.connectors import zoominfo as zi
from app.connectors import salesforce as sf
from app.utils.dedupe import normalize, fuzzy_dedupe
from app.utils.sales_navigator_csv import accounts_csv

def run_pipeline(params: Dict, ui_decisions: Dict) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Orchestrates the mock end-to-end pipeline:
      Similarweb (mock) → Normalize & Dedupe → Salesforce check (mock)
      → ZoomInfo personas (mock) → optional Sales Navigator personas (mock)
      → Sales Navigator CSV + final Excel (with CSV fallback).
    Returns:
      companies (DataFrame), leads_df (DataFrame), companies_no_personas (DataFrame)
    """

    # --- Mini Mode: deterministic seed for reproducible demos ---
    if params.get("mini_mode"):
        import random
        random.seed(42)
        try:
            import numpy as np
            np.random.seed(42)
        except Exception:
            pass

    # 1) Similarweb (mock search)
    raw = sw.search_companies(
        params["verticals"],
        params["countries"],
        params["min_monthly_visits"],
    )

    # 2) Normalize & Dedupe (stdlib difflib inside fuzzy_dedupe)
    norm = normalize(raw)
    deduped = fuzzy_dedupe(norm, threshold=0.92)

    # Cap to 5 companies in Mini Mode
    if params.get("mini_mode"):
        deduped = deduped.head(5).reset_index(drop=True)

    # Optional UI overrides: keep specific domains
    if ui_decisions.get("keep_domains"):
        extra = norm[norm["domain"].isin(ui_decisions["keep_domains"])]
        deduped = (
            pd.concat([deduped, extra])
            .drop_duplicates(subset=["domain"])
            .reset_index(drop=True)
        )

    # 3) Salesforce check (mock) — SAFE FALLBACKS
    lookup_fn = getattr(sf, "find_account_by_domain", None)
    if callable(lookup_fn):
        deduped["sf_account_id"] = deduped["domain"].apply(lookup_fn)
    else:
        deduped["sf_account_id"] = None

    # Optional: create new SF accounts (mock) for selected domains — SAFE FALLBACK
    create_fn = getattr(sf, "create_account", None)
    if callable(create_fn):
        for d in ui_decisions.get("create_sf_accounts", []):
            idx = deduped.index[deduped["domain"] == d]
            if len(idx):
                deduped.loc[idx, "sf_account_id"] = create_fn(
                    deduped.loc[idx[0], "company_name"], d
                )

    # 4) ZoomInfo enrichment + personas (mock)
    enriched_rows = []
    leads_frames = []
    for _, row in deduped.iterrows():
        z = zi.enrich_company(row["domain"])
        li_url = z.get("linkedin_url") if z else None
        zi_id = z.get("id") if z else None

        ppl = (
            zi.find_personas(
                zi_id,
                params.get("titles_regex", ""),
                row.get("country"),
                row["domain"],
                enable_email_enrichment=params.get("enable_zoominfo_email_enrichment", True),
            )
            if zi_id
            else pd.DataFrame()
        )
        if not ppl.empty:
            leads_frames.append(ppl)

        enriched_rows.append(
            {
                **row.to_dict(),
                "zoominfo_company_id": zi_id,
                "li_company_url": li_url,
            }
        )

    companies = pd.DataFrame(enriched_rows)
    leads_df = (
        pd.concat(leads_frames, ignore_index=True)
        if leads_frames
        else pd.DataFrame(
            columns=["company_domain", "full_name", "title", "email", "li_profile", "source", "confidence"]
        )
    )

    # Companies still needing Sales Navigator (no personas from ZoomInfo)
    companies_no_personas = companies[~companies["domain"].isin(leads_df["company_domain"])]

    # 4b) OPTIONAL: Sales Navigator personas (emails must remain blank)
    if params.get("use_sales_navigator_mock"):
        try:
            from app.connectors.sales_navigator import find_personas_from_account_list
            # Include SN leads for ALL companies, filtered by the same titles regex
            sn_domains = companies["domain"].tolist()
            sn_leads = find_personas_from_account_list(sn_domains, params.get("titles_regex", ""))
            if not sn_leads.empty:
                leads_df = pd.concat([leads_df, sn_leads], ignore_index=True)
        except Exception as e:
            # Non-fatal: just log; pipeline continues
            print(f"[WARN] Sales Navigator mock unavailable: {e}")

    # --- Ensure output directory exists (Streamlit Cloud safe) ---
    os.makedirs("data/outputs", exist_ok=True)

    # 5) Sales Navigator CSV
    accounts_csv(companies_no_personas, "data/outputs/sn_accounts_upload.csv")

    # 6) Final Excel with three sheets (prefer XlsxWriter; fallback to CSVs)
    try:
        with pd.ExcelWriter("data/outputs/final.xlsx", engine="xlsxwriter") as xl:
            companies.to_excel(xl, sheet_name="Companies", index=False)
            leads_df.to_excel(xl, sheet_name="Leads", index=False)
            companies_no_personas.to_excel(xl, sheet_name="Needs_SalesNav", index=False)
    except Exception as e:
        # Fallback: write separate CSVs so the app still provides downloads
        companies.to_csv("data/outputs/final_companies.csv", index=False)
        leads_df.to_csv("data/outputs/final_leads.csv", index=False)
        companies_no_personas.to_csv("data/outputs/final_needs_salesnav.csv", index=False)
        print(f"[WARN] Failed to write XLSX with XlsxWriter: {e}. Wrote CSV fallbacks instead.")

    return companies, leads_df, companies_no_personas
