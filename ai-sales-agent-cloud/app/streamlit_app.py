import sys, os
# ensure correct import path on Streamlit Cloud
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from app.agent_orchestrator import run_pipeline
from app.utils.sales_navigator_csv import accounts_csv

st.set_page_config(page_title='AI Sales Agent (Cloud)', layout='wide')
st.title('🧠 AI Sales Agent – Streamlit Cloud')
st.caption('Similarweb → ZoomInfo → Salesforce → Sales Navigator (Mocks)')
with st.sidebar:
    st.header('Eingabemaske')
    verticals=st.multiselect('Verticals',['SaaS','Ecommerce','Fintech'], default=['SaaS'])
    countries_str=st.text_input('Länder (Komma-separiert)','DE,AT,CH')
    min_visits=st.number_input('Mindest-Monatsvisits', min_value=1000, value=50000, step=5000)
    titles_regex=st.text_input('Persona/Titel Regex','(Head|VP|Director) (Marketing|Sales|Growth|Demand Gen)')
    mini_mode=st.checkbox('Mini-Modus (≤5 Firmen, fixer Seed)', value=True)
    run=st.button('Pipeline ausführen')
    st.markdown('---'); st.subheader('Sales Navigator'); dl_sn=st.button('SN CSV neu erzeugen')
st.markdown('---'); st.markdown('### 🔍 Schritt 1: Similarweb → Normalize & Dedupe')
if 'companies' not in st.session_state:
    st.session_state.companies=pd.DataFrame(); st.session_state.leads=pd.DataFrame(); st.session_state.needs_sn=pd.DataFrame()
st.markdown('### ⚙️ Human-in-the-Loop')
with st.expander('Dedupe/Overrides'):
    keep_domains=st.text_input('Domains trotz Fuzzy-Dupe behalten (Komma-separiert)','')
with st.expander('Salesforce: Neue Accounts anlegen'):
    create_accounts=st.text_input('Domains (Komma-separiert) für neue SF-Accounts','')
ui={'keep_domains':[d.strip() for d in keep_domains.split(',') if d.strip()], 'create_sf_accounts':[d.strip() for d in create_accounts.split(',') if d.strip()]}
if run:
    params={'verticals':verticals,'countries':[c.strip().upper() for c in countries_str.split(',') if c.strip()], 'min_monthly_visits':int(min_visits), 'titles_regex':titles_regex, 'mini_mode':bool(mini_mode)}
    with st.spinner('Pipeline läuft...'):
        companies, leads, needs = run_pipeline(params, ui)
    st.session_state.companies, st.session_state.leads, st.session_state.needs_sn = companies, leads, needs
    st.success('Pipeline abgeschlossen!')
if not st.session_state.companies.empty:
    st.subheader('🏢 Companies'); st.dataframe(st.session_state.companies, use_container_width=True)
    st.subheader('👥 Leads'); st.dataframe(st.session_state.leads, use_container_width=True)
    st.subheader('📋 Firmen ohne Personas → Sales Navigator Upload'); st.dataframe(st.session_state.needs_sn, use_container_width=True)
    st.download_button('📥 Download final.xlsx', data=open('data/outputs/final.xlsx','rb'), file_name='final.xlsx')
    st.download_button('📥 Download sn_accounts_upload.csv', data=open('data/outputs/sn_accounts_upload.csv','rb'), file_name='sn_accounts_upload.csv')
if dl_sn and not st.session_state.companies.empty:
    accounts_csv(st.session_state.needs_sn, 'data/outputs/sn_accounts_upload.csv')
    st.success('SN CSV neu erzeugt.')
    st.download_button('📥 Download sn_accounts_upload.csv', data=open('data/outputs/sn_accounts_upload.csv','rb'), file_name='sn_accounts_upload.csv')
