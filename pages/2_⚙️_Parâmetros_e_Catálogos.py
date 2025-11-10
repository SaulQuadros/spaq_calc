import streamlit as st, pandas as pd
from src.spaq.utils.session import set_state_defaults
from src.spaq.io.parsers import load_builtin_heaters, read_catalog_csv
st.set_page_config(page_title='Parâmetros', page_icon='⚙️', layout='wide')
st.title('⚙️ Parâmetros & Catálogos')
set_state_defaults(method='max_possible', K=1.0, T_in_C=20.0, T_set_C=40.0, derate=1.0, margin=0.10, heater_catalog=load_builtin_heaters(), chosen_model=None)
method = st.radio('Método', ['max_possible','max_prob'], format_func=lambda s: 'Máx. possível (100%)' if s=='max_possible' else 'Máx. provável (K·√Σpesos)')
st.session_state.method = method
c1,c2,c3 = st.columns(3)
with c1: st.session_state.T_in_C = st.number_input('T_in (°C)', value=st.session_state.T_in_C, step=1.0)
with c2: st.session_state.T_set_C = st.number_input('T_set (°C)', value=st.session_state.T_set_C, step=1.0)
with c3: st.session_state.derate = st.number_input('Derate', value=st.session_state.derate, step=0.05, min_value=0.5, max_value=1.1)
st.session_state.margin = st.slider('Margem (%)', 0, 30, int(st.session_state.margin*100))/100.0
st.subheader('Catálogo (exemplo)')
up = st.file_uploader('Upload CSV catálogo (opcional)', type=['csv'])
if up: st.session_state.heater_catalog = read_catalog_csv(up)
st.dataframe(st.session_state.heater_catalog, use_container_width=True)
models = st.session_state.heater_catalog['model'].tolist()
st.session_state.chosen_model = st.selectbox('Modelo', models, index=0 if models else None)
