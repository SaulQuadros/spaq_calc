
import streamlit as st
import pandas as pd
from src.spaq.calcs.checks import check_min_flow_on, check_p_min_dyn, pressure_budget_messages

st.set_page_config(page_title="Validações & Diagnósticos", page_icon="🧪", layout="wide")
st.title("🧪 Validações & Diagnósticos")

points = st.session_state.get("points_df", pd.DataFrame())
catalog = st.session_state.get("heater_catalog", pd.DataFrame())
res = st.session_state.get("results", None)

if points.empty or catalog.empty or not res:
    st.warning("Calcule o dimensionamento e selecione ao menos um modelo.")
    st.stop()

model = res.get("model")
row = catalog[catalog["model"] == model].iloc[0]

st.subheader("Validações básicas")
msgs = []
msgs += check_min_flow_on(points, row["q_min_on_lpm"])
msgs += check_p_min_dyn(points, row["p_min_dyn_kpa"])
if not msgs:
    st.success("Nenhum problema encontrado nas validações básicas.")
else:
    for msg in msgs:
        st.warning("• " + msg)

st.subheader("Balanço de Pressão (simplificado)")
supply_dyn = st.number_input("Pressão dinâmica disponível a montante do aquecedor (kPa)", value=250.0, step=10.0)
mixer_dp = st.number_input("Perda típica no misturador (kPa)", value=20.0, step=5.0)
q_per_unit = float(res.get("q_per_unit", 0.0))
pb_msgs = pressure_budget_messages(points, row, q_per_unit, supply_dyn_kpa=supply_dyn, mixer_dp_kpa=mixer_dp)
for m in pb_msgs:
    if m.startswith("OK"):
        st.success(m)
    elif m.startswith("NÃO OK"):
        st.error(m)
    else:
        st.info(m)
