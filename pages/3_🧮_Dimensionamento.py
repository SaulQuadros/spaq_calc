
import streamlit as st
import pandas as pd
from src.spaq.utils.session import set_state_defaults
from src.spaq.calcs.thermal import dT_proj, power_from_Q_dT, q_unit_eff, power_unit_eff
from src.spaq.calcs.deterministic import Q_max_possible
from src.spaq.calcs.probabilistic import Q_max_prob
from src.spaq.select.chooser import choose_units

st.set_page_config(page_title="Dimensionamento", page_icon="🧮", layout="wide")
st.title("🧮 Dimensionamento")

set_state_defaults()
points = st.session_state.get("points_df", pd.DataFrame())
method = st.session_state.get("method", "max_possible")
T_in = float(st.session_state.get("T_in_C", 20.0))
T_set = float(st.session_state.get("T_set_C", 40.0))
derate = float(st.session_state.get("derate", 1.0))
margin = float(st.session_state.get("margin", 0.10))
catalog = st.session_state.get("heater_catalog", pd.DataFrame())
chosen_models = st.session_state.get("chosen_models", [])

if points.empty or catalog.empty or not chosen_models:
    st.warning("Forneça pontos e selecione ao menos um modelo na página ⚙️ Parâmetros & Catálogos.")
    st.stop()

if method == "max_possible":
    Q_tot = Q_max_possible(points)
else:
    K = float(st.session_state.get("K", 1.0))
    weights = {k: float(v) for k, v in st.session_state.get("weights", {"chuveiro": 4.0, "lavatório": 1.0, "cozinha": 2.0}).items()}
    Q_tot = Q_max_prob(points, K=K, weights=weights)

dT = dT_proj(T_in, T_set)
P_req = power_from_Q_dT(Q_tot, dT)

rows = []
for model in chosen_models:
    row = catalog[catalog["model"] == model].iloc[0]
    Q_ref = float(row["q_ref_lpm"]); dT_ref = float(row["dT_ref_C"]); P_nom = float(row["power_kw"])
    q_eff = q_unit_eff(Q_ref, dT_ref, dT, derate=derate)
    p_eff = power_unit_eff(P_nom, derate=derate)
    N_flow, N_power, N_final, q_per_unit = choose_units(Q_tot*(1+margin), dT, q_eff, p_eff)
    rows.append({
        "model": model,
        "q_unit_eff_lpm": q_eff,
        "power_unit_eff_kw": p_eff,
        "N_by_flow": N_flow,
        "N_by_power": N_power,
        "N_final": N_final,
        "q_per_unit": q_per_unit
    })

df = pd.DataFrame(rows).sort_values(["N_final","N_by_flow","N_by_power","model"]).reset_index(drop=True)

st.subheader("Resumo do Cenário")
st.write({"method": method, "Q_tot_lpm": Q_tot, "ΔT": dT, "P_req_kw": P_req, "derate": derate, "margin": margin})

st.subheader("Comparação de Modelos")
st.dataframe(df, use_container_width=True)

# Eleger o primeiro da lista como 'selecionado' para as próximas páginas
if not df.empty:
    best = df.iloc[0].to_dict()
    st.session_state.results = {
        "Q_tot_lpm": Q_tot,
        "dT_proj_C": dT,
        "power_req_kw": P_req,
        **best
    }
    st.success(f"Modelo recomendado (provisório): {best['model']} — N_final = {int(best['N_final'])}")
