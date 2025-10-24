# app/streamlit_app.py
import sys, os, io
# Ensure imports work on Streamlit Cloud (add repo root to PYTHONPATH)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd

from app.agent_orchestrator import run_pipeline
from app.utils.sales_navigator_csv import accounts_csv


def make_excel_bytes(companies: pd.DataFrame, leads: pd.DataFrame, needs_sn: pd.DataFrame):
    """Try to generate an XLSX in memory. Return bytes or None on failure."""
    try:
        bio = io.BytesIO()
        with pd.ExcelWriter(bio, engine="xlsxwriter") as xl:
            companies.to_excel(xl, sheet_name="Companies", index=False)
            leads.to_excel(xl, sheet_name="Leads", index=False)
            needs_sn.to_excel(xl, sheet_name="Needs_SalesNav", index=False)
        bio.seek(0)
        return bio.getvalue()
    except Exception as e:
        print(f"[WARN] Could not build in-memory XLSX: {e}")
        return None


st.set_page_config(page_title='AI Sales Agent (Cloud)', layout='wide')

st.title('🧠 AI Sales Agent – Streamlit Cloud')
st.caption('Similarweb → ZoomInfo → Salesforce → Sales Navigator (Mocks, Mini mode supported)')

with st.sidebar:
    st.header('Input')
    verticals = st.multiselect('Verticals', ['SaaS', 'Ecommerce', 'Fintech'], default=['SaaS'])
    countries_str = st.text_input('Countries (comma-separated)', 'DE,AT,CH')
    min_visits = st.number_input('Min monthly visits', min_value=1000, value=50000, step=5000)
    titles_regex = st.text_input('Persona/Title Regex', '(Head|VP|Director) (Marketing|Sales|Growth|Demand Gen)')
    mini_mode = st.checkbox('Mini mode (≤5 companies, fixed seed)', value=True)

    st.markdown('---')
    st.subheader('Lead Enrichment Options')
    enrich_emails_zoominfo = st.checkbox('Enrich emails from ZoomInfo', value=True)
    include_sn_leads = st.checkbox('Include Sales Navigator mock leads', value=False)

    st.markdown('---')
    run = st.button('Run pipeline')

st.markdown('---')
st.markdown('### 🔍 Similarweb → Normalize & Dedupe')

# Session state containers
if 'companies' not in st.session_state:
    st.session_state.companies = pd.DataFrame()
    st.session_state.leads = pd.DataFrame()
    st.session_state.needs_sn = pd.DataFrame()

st.markdown('### ⚙️ Human-in-the-Loop')
with st.expander('Dedupe/Overrides'):
    keep_domains = st.text_input('Domains to keep despite fuzzy-dedupe (comma-separated)', '')
with st.expander('Salesforce: Create new accounts'):
    create_accounts = st.text_input('Domains (comma-separated) to create new SF accounts for', '')

ui = {
    'keep_domains': [d.strip() for d in keep_domains.split(',') if d.strip()],
    'create_sf_accounts': [d.strip() for d in create_accounts.split(',') if d.strip()],
}

if run:
    params = {
        'verticals': verticals,
        'countries': [c.strip().upper() for c in countries_str.split(',') if c.strip()],
        'min_monthly_visits': int(min_visits),
        'titles_regex': titles_regex,
        'mini_mode': bool(mini_mode),

        # toggles:
        'enable_zoominfo_email_enrichment': bool(enrich_emails_zoominfo),
        'use_sales_navigator_mock': bool(include_sn_leads),
    }
    with st.spinner('Running pipeline...'):
        companies, leads, needs = run_pipeline(params, ui)
    st.session_state.companies = companies
    st.session_state.leads = leads
    st.session_state.needs_sn = needs
    st.success('Pipeline completed.')

if not st.session_state.companies.empty:
    st.subheader('🏢 Companies')
    st.dataframe(st.session_state.companies, use_container_width=True)

    st.subheader('👥 Leads')
    # Show only the most relevant columns in the Leads table
    preferred_cols = ["company_domain", "full_name", "title", "email", "li_profile", "source"]
    existing_cols = [c for c in preferred_cols if c in st.session_state.leads.columns]
    if existing_cols:
        leads_view = st.session_state.leads[existing_cols].copy()
        st.dataframe(leads_view, use_container_width=True)
    else:
        # Fallback: show whatever we have
        st.dataframe(st.session_state.leads, use_container_width=True)

    st.caption("Legend: ZoomInfo leads may include emails (if enabled). Sales Navigator leads have blank email but include a LinkedIn profile URL.")

    st.subheader('📋 Accounts needing Sales Navigator')
    st.dataframe(st.session_state.needs_sn, use_container_width=True)

    # ====== Download buttons (robust) ======
    st.markdown('---')
    st.subheader('📥 Downloads')

    # Try in-memory XLSX first (works even if the file on disk is absent)
    xlsx_bytes = make_excel_bytes(
        st.session_state.companies, st.session_state.leads, st.session_state.needs_sn
    )
    if xlsx_bytes:
        st.download_button('📥 Download final.xlsx', data=xlsx_bytes, file_name='final.xlsx')
    else:
        # CSV fallbacks
        st.info("Could not build Excel workbook in this environment. Offering CSV downloads instead.")
        st.download_button(
            '📥 final_companies.csv',
            data=st.session_state.companies.to_csv(index=False).encode('utf-8'),
            file_name='final_companies.csv',
            mime='text/csv'
        )
        st.download_button(
            '📥 final_leads.csv',
            data=st.session_state.leads.to_csv(index=False).encode('utf-8'),
            file_name='final_leads.csv',
            mime='text/csv'
        )
        st.download_button(
            '📥 final_needs_salesnav.csv',
            data=st.session_state.needs_sn.to_csv(index=False).encode('utf-8'),
            file_name='final_needs_salesnav.csv',
            mime='text/csv'
        )

    # Sales Navigator CSV (prefer on-disk if exists; else generate on the fly)
    sn_path = 'data/outputs/sn_accounts_upload.csv'
    if os.path.exists(sn_path):
        with open(sn_path, 'rb') as f:
            st.download_button('📥 sn_accounts_upload.csv', data=f.read(), file_name='sn_accounts_upload.csv')
    else:
        # Build from in-memory DataFrame
        sn_csv = st.session_state.needs_sn.copy()
        out = pd.DataFrame({
            'Company Name': sn_csv.get('company_name', sn_csv.get('domain', pd.Series([], dtype=str))).fillna(sn_csv.get('domain')),
            'Company Website': sn_csv.get('company_url', 'https://') + sn_csv.get('domain', pd.Series([], dtype=str)),
            'Company LinkedIn URL': sn_csv.get('li_company_url', pd.Series(['']*len(sn_csv))),
            'Country': sn_csv.get('hq_country', sn_csv.get('country', pd.Series(['']*len(sn_csv)))),
        })
        st.download_button(
            '📥 sn_accounts_upload.csv',
            data=out.to_csv(index=False).encode('utf-8'),
            file_name='sn_accounts_upload.csv',
            mime='text/csv'
        )
