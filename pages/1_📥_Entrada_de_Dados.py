import streamlit as st, pandas as pd
from src.spaq.utils.session import set_state_defaults
st.set_page_config(page_title='Entrada', page_icon='📥', layout='wide')
set_state_defaults(points_df=pd.DataFrame([
 {'name':'Chuveiro 1','kind':'chuveiro','flow_lpm':12.0,'p_min_dyn_kpa':100,'count':1},
 {'name':'Chuveiro 2','kind':'chuveiro','flow_lpm':12.0,'p_min_dyn_kpa':100,'count':1},
 {'name':'Lavatório 1','kind':'lavatório','flow_lpm':5.0,'p_min_dyn_kpa':70,'count':1},
 {'name':'Cozinha 1','kind':'cozinha','flow_lpm':10.0,'p_min_dyn_kpa':80,'count':1},
]))
st.title('📥 Entrada de Dados')
points_df = st.data_editor(st.session_state.points_df, num_rows='dynamic', use_container_width=True)
st.session_state.points_df = points_df
st.download_button('⬇️ Baixar pontos (CSV)', data=points_df.to_csv(index=False).encode('utf-8'), file_name='spaq_pontos.csv')
