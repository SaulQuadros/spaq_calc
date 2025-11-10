
import streamlit as st
import pandas as pd
from src.spaq.calcs.network import dp_darcy_weissbach, dp_minors

st.set_page_config(page_title="Hidráulica (Perdas de Rede)", page_icon="🔧", layout="wide")
st.title("🔧 Hidráulica — Perdas de Rede (tubos + acessórios)")

st.markdown("""Defina a **linha crítica** em trechos sequenciais. O App calcula Δp (kPa) por Darcy-Weisbach
e somas localizadas (ΣK·v²/2g). O resultado pode ser integrado ao **Balanço de Pressão** em *Validações & Diagnósticos*.""")

# Fluxo de projeto adotado para cálculo
flow_mode = st.radio("Vazão para cálculo dos trechos", ["Q_tot do cenário", "Q_por_unidade (por aquecedor)", "Valor personalizado"])
Q_custom = st.number_input("Se 'Valor personalizado', informe Q (L/min)", value=0.0, step=1.0)
res = st.session_state.get("results", {})
Q_tot = float(res.get("Q_tot_lpm", 0.0))
Q_unit = float(res.get("q_per_unit", 0.0))
if flow_mode == "Q_tot do cenário":
    Q_use = Q_tot
elif flow_mode == "Q_por_unidade (por aquecedor)":
    Q_use = Q_unit
else:
    Q_use = Q_custom

st.info(f"Vazão adotada para cálculo: **{Q_use:.2f} L/min**")

# Tabela de trechos
if "network_segments" not in st.session_state:
    st.session_state.network_segments = pd.DataFrame([
        {"trecho":"T1","comprimento_m":10.0,"diametro_mm":25.0,"material":"PVC","K_local":2.0},
        {"trecho":"T2","comprimento_m":6.0,"diametro_mm":25.0,"material":"PVC","K_local":4.0},
    ])

seg_df = st.data_editor(
    st.session_state.network_segments,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "material": st.column_config.SelectboxColumn(options=["PVC","CPVC","PEX","cobre","aço galvanizado","ferro fundido"])
    }
)
st.session_state.network_segments = seg_df

temp_C = st.number_input("Temperatura de cálculo (°C)", value=40.0, step=1.0)

# Cálculo
rows = []
dp_total = 0.0
for _, r in seg_df.iterrows():
    L = float(r["comprimento_m"]); Dmm = float(r["diametro_mm"]); mat = str(r["material"]); K = float(r["K_local"])
    dp_fric_kpa, dbg = dp_darcy_weissbach(Q_use, L, Dmm, material=mat, temp_C=temp_C)
    dp_loc_kpa = dp_minors(Q_use, Dmm, K, temp_C=temp_C)
    dp_seg = dp_fric_kpa + dp_loc_kpa
    dp_total += dp_seg
    rows.append({
        "trecho": r["trecho"],
        "Δp_fric_kPa": round(dp_fric_kpa,2),
        "Δp_local_kPa": round(dp_loc_kpa,2),
        "Δp_total_kPa": round(dp_seg,2),
        "Re": round(dbg["Re"],0),
        "f": round(dbg["f"],5),
        "v_m_s": round(dbg["v"],3),
    })

out = pd.DataFrame(rows)
st.subheader("Resultados por trecho")
st.dataframe(out, use_container_width=True)

st.metric("Δp_total (rede) — kPa", f"{dp_total:.1f}")
st.session_state.dp_network_kpa = float(dp_total)
st.success("Perda de rede salva na sessão como **dp_network_kpa**. Ela será usada no Balanço de Pressão.")
