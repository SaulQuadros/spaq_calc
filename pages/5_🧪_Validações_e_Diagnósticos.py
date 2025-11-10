import streamlit as st, pandas as pd
from src.spaq.calcs.checks import check_min_flow_on, check_p_min_dyn
st.set_page_config(page_title='Validações', page_icon='🧪', layout='wide')
st.title('🧪 Validações & Diagnósticos')
points = st.session_state.get('points_df', pd.DataFrame())
catalog = st.session_state.get('heater_catalog', pd.DataFrame())
model = st.session_state.get('chosen_model', None)
if points.empty or catalog.empty or not model: st.warning('Forneça pontos e selecione um modelo.'); st.stop()
row = catalog[catalog['model']==model].iloc[0]
msgs = []; msgs += check_min_flow_on(points, row['q_min_on_lpm']); msgs += check_p_min_dyn(points, row['p_min_dyn_kpa'])
if not msgs: st.success('Nenhum problema básico encontrado.')
else:
    for m in msgs: st.warning('• ' + m)
