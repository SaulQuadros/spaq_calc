
import streamlit as st
import pandas as pd
from src.spaq.utils.session import set_state_defaults
from src.spaq.io.parsers import load_builtin_heaters, read_catalog_csv, load_presets_yaml

st.set_page_config(page_title="Parâmetros & Catálogos", page_icon="⚙️", layout="wide")
st.title("⚙️ Parâmetros & Catálogos")

presets = load_presets_yaml()

set_state_defaults(
    method="max_possible",  # "max_possible" | "max_prob"
    K=1.0,
    weights={"chuveiro": 4.0, "lavatório": 1.0, "cozinha": 2.0},
    T_in_C=20.0,
    T_set_C=40.0,
    derate=1.0,
    margin=0.10,
    heater_catalog=load_builtin_heaters(),
    chosen_models=[],  # multiselect
)

method = st.radio("Método de dimensionamento", ["max_possible", "max_prob"],
                  format_func=lambda s: "Máx. possível (100%)" if s=="max_possible" else "Máx. provável (K·√Σpesos)")
st.session_state.method = method

c1, c2, c3 = st.columns(3)
with c1:
    st.session_state.T_in_C = st.number_input("T_in (°C)", value=st.session_state.T_in_C, step=1.0)
with c2:
    st.session_state.T_set_C = st.number_input("T_set (°C)", value=st.session_state.T_set_C, step=1.0)
with c3:
    st.session_state.derate = st.number_input("Derate (fator)", value=st.session_state.derate, step=0.05, min_value=0.5, max_value=1.1)

st.session_state.margin = st.slider("Margem adicional (%)", min_value=0, max_value=30, value=int(st.session_state.margin*100)) / 100.0

st.subheader("Catálogo de Aquecedores (exemplo)")
st.caption("Substitua por dados oficiais dos fabricantes para projeto real.")
uploaded = st.file_uploader("Upload CSV catálogo (opcional)", type=["csv"])
if uploaded:
    st.session_state.heater_catalog = read_catalog_csv(uploaded)

st.dataframe(st.session_state.heater_catalog, use_container_width=True)

# Multiselect de modelos
models = st.session_state.heater_catalog["model"].tolist()
chosen = st.multiselect("Modelo(s) para dimensionamento", models, default=models[:1])
st.session_state.chosen_models = chosen

# Presets para Máx. provável
if method == "max_prob":
    st.markdown("### Presets (K & Pesos)")
    profile_names = list(presets.get("profiles", {}).keys())
    if profile_names:
        prof = st.selectbox("Perfil", profile_names, index=0)
        prof_data = presets["profiles"][prof]
        st.session_state.K = float(prof_data.get("K", 1.0))
        st.session_state.weights = {**st.session_state.weights, **prof_data.get("weights", {})}
        st.info(f"K do perfil: {st.session_state.K}")

    # Editor de pesos
    weights_df = pd.DataFrame([
        {"tipo": k, "peso": float(v)} for k, v in st.session_state.weights.items()
    ])
    weights_df = st.data_editor(weights_df, num_rows="dynamic", use_container_width=True)
    st.session_state.weights = {row["tipo"]: float(row["peso"]) for _, row in weights_df.iterrows()}

    st.session_state.K = st.number_input("K (ajuste fino)", value=float(st.session_state.K), step=0.05, min_value=0.1)
