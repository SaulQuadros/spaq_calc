import streamlit as st, pandas as pd
st.set_page_config(page_title='Resultados', page_icon='📊', layout='wide')
st.title('📊 Resultados & Relatório')
res = st.session_state.get('results', None)
if not res: st.info('Calcule primeiro na página 🧮 Dimensionamento.'); st.stop()
st.json(res)
df_out = pd.DataFrame([res])
st.download_button('⬇️ Baixar Resultado (CSV)', data=df_out.to_csv(index=False).encode('utf-8'), file_name='spaq_resultado.csv')
