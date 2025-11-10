
import streamlit as st
import pandas as pd
from src.spaq.calcs.network import dp_darcy_weissbach, dp_minors
from src.spaq.calcs.network_tree import compute_dp_on_edges, path_dp_to_sinks

st.set_page_config(page_title="Hidráulica (Perdas de Rede)", page_icon="🔧", layout="wide")
st.title("🔧 Hidráulica — Perdas de Rede (linha crítica ou rede ramificada)")

mode = st.radio("Modo de cálculo", ["Linha crítica única", "Rede ramificada (árvore)"], horizontal=True)

# Base de vazões
res = st.session_state.get("results", {})
Q_tot = float(res.get("Q_tot_lpm", 0.0))
Q_unit = float(res.get("q_per_unit", 0.0))
flow_mode = st.radio("Vazão adotada", ["Q_tot do cenário", "Q_por_unidade (por aquecedor)", "Valor personalizado"], horizontal=True)
Q_custom = st.number_input("Se 'Valor personalizado', informe Q (L/min)", value=0.0, step=1.0)
Q_use = Q_tot if flow_mode=="Q_tot do cenário" else (Q_unit if flow_mode=="Q_por_unidade (por aquecedor)" else Q_custom)
st.info(f"Vazão adotada: **{Q_use:.2f} L/min**")
temp_C = st.number_input("Temperatura de cálculo (°C)", value=40.0, step=1.0)

if mode == "Linha crítica única":
    if "network_segments" not in st.session_state:
        st.session_state.network_segments = pd.DataFrame([
            {"trecho":"T1","comprimento_m":10.0,"diametro_mm":25.0,"material":"PVC","K_local":2.0},
            {"trecho":"T2","comprimento_m":6.0,"diametro_mm":25.0,"material":"PVC","K_local":4.0},
        ])
    seg_df = st.data_editor(
        st.session_state.network_segments,
        num_rows="dynamic",
        use_container_width=True,
        column_config={"material": st.column_config.SelectboxColumn(options=["PVC","CPVC","PEX","cobre","aço galvanizado","ferro fundido"])}
    )
    st.session_state.network_segments = seg_df

    rows, dp_total = [], 0.0
    for _, r in seg_df.iterrows():
        L = float(r["comprimento_m"]); Dmm = float(r["diametro_mm"]); mat = str(r["material"]); K = float(r["K_local"])
        dp_fric_kpa, dbg = dp_darcy_weissbach(Q_use, L, Dmm, material=mat, temp_C=temp_C)
        dp_loc_kpa = dp_minors(Q_use, Dmm, K, temp_C=temp_C)
        dp_seg = dp_fric_kpa + dp_loc_kpa
        dp_total += dp_seg
        rows.append({"trecho": r["trecho"], "Δp_fric_kPa": round(dp_fric_kpa,2), "Δp_local_kPa": round(dp_loc_kpa,2), "Δp_total_kPa": round(dp_seg,2), "v_m_s": round(dbg["v"],3)})
    out = pd.DataFrame(rows)
    st.subheader("Resultados por trecho")
    st.dataframe(out, use_container_width=True)
    st.metric("Δp_total (rede) — kPa", f"{dp_total:.1f}")
    st.session_state.dp_network_kpa = float(dp_total)
    st.success("Perda de rede salva como dp_network_kpa.")

else:
    st.markdown("### Nós")
    if "net_nodes" not in st.session_state:
        st.session_state.net_nodes = pd.DataFrame([
            {"node_id":"A","demand_lpm":0.0},
            {"node_id":"B","demand_lpm":10.0},
            {"node_id":"C","demand_lpm":12.0},
        ])
    nodes_df = st.data_editor(st.session_state.net_nodes, num_rows="dynamic", use_container_width=True)
    st.session_state.net_nodes = nodes_df

    st.markdown("### Trechos (arestas)")
    if "net_edges" not in st.session_state:
        st.session_state.net_edges = pd.DataFrame([
            {"from_node":"A","to_node":"B","comprimento_m":10.0,"diametro_mm":25.0,"material":"PVC","K_local":2.0},
            {"from_node":"A","to_node":"C","comprimento_m":8.0,"diametro_mm":25.0,"material":"PVC","K_local":2.0},
        ])
    edges_df = st.data_editor(
        st.session_state.net_edges, num_rows="dynamic", use_container_width=True,
        column_config={"material": st.column_config.SelectboxColumn(options=["PVC","CPVC","PEX","cobre","aço galvanizado","ferro fundido"])}
    )
    st.session_state.net_edges = edges_df

    st.caption("Dica: a soma das demandas nos nós terminais deve se aproximar da vazão de projeto do cenário.")

    edge_df, flows = compute_dp_on_edges(nodes_df, edges_df, temp_C=temp_C)
    st.subheader("Resultados por trecho (com Q distribuído)")
    st.dataframe(edge_df.round({"Δp_fric_kPa":2,"Δp_local_kPa":2,"Δp_total_kPa":2,"v_m_s":3}), use_container_width=True)

    sink_rows = path_dp_to_sinks(edge_df, nodes_df, edges_df)
    if sink_rows:
        crit = max(sink_rows, key=lambda r: r["Δp_path_kPa"])
        st.info(f"Caminho crítico até o nó {crit['sink']}: Δp = {crit['Δp_path_kPa']:.1f} kPa — edges: {crit['edges']}")
        st.session_state.dp_network_kpa = float(crit["Δp_path_kPa"])
        st.success("Perda de rede (caminho crítico) salva como dp_network_kpa.")
    else:
        st.warning("Não foi possível identificar nós terminais (sinks). Verifique a conectividade da rede.")
