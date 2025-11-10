
import pandas as pd
from .hydraulics import dp_heater_at_q

def check_min_flow_on(points_df: pd.DataFrame, q_min_on_lpm: float):
    msgs = []
    for _, r in points_df.iterrows():
        if float(r["flow_lpm"]) < float(q_min_on_lpm):
            msgs.append(f"{r['name']}: vazão {r['flow_lpm']} L/min < vazão mínima de acionamento ({q_min_on_lpm} L/min).")
    return msgs

def check_p_min_dyn(points_df: pd.DataFrame, p_min_dyn_kpa_model: float):
    msgs = []
    for _, r in points_df.iterrows():
        if float(r["p_min_dyn_kpa"]) < float(p_min_dyn_kpa_model):
            msgs.append(f"{r['name']}: pressão mínima no ponto {r['p_min_dyn_kpa']} kPa < exigida pelo modelo ({p_min_dyn_kpa_model} kPa).")
    return msgs

def pressure_budget_messages(points_df: pd.DataFrame, model_row, q_per_unit_lpm: float, supply_dyn_kpa: float, mixer_dp_kpa: float = 20.0, dp_curve_override: dict = None):
    """Relatório simples de viabilidade de pressão considerando:
    supply_dyn_kpa (pressão disponível a montante do aquecedor),
    p_min_dyn_kpa (requisito do modelo),
    dp_heater(q_per_unit) (perda no trocador),
    mixer_dp_kpa (perda típica no misturador).
    Não inclui perdas de rede (tubulação) — pode ser somado externamente.
    """
    msgs = []
    try:
        dp_curve = dict(dp_curve_override or {})
        # também aceitar colunas 'dp_lpm_X_kpa' no catálogo
        for col in ["dp_lpm_8_kpa","dp_lpm_10_kpa","dp_lpm_12_kpa"]:
            if col in model_row and not pd.isna(model_row[col]):
                lpm = int(col.split("_")[2])
                dp_curve.setdefault(float(lpm), float(model_row[col]))

        dp_q = dp_heater_at_q(dp_curve, float(q_per_unit_lpm)) if dp_curve else 0.0
        required_upstream = float(model_row["p_min_dyn_kpa"]) + float(dp_q) + float(mixer_dp_kpa)
        ok = float(supply_dyn_kpa) >= required_upstream
        headroom = float(supply_dyn_kpa) - required_upstream

        msg = f"Pressão montante {supply_dyn_kpa:.1f} kPa; requisito (modelo + Δp_aquecedor@{q_per_unit_lpm:.1f} L/min + misturador) = {required_upstream:.1f} kPa → margem = {headroom:.1f} kPa."
        if ok:
            msgs.append("OK: " + msg)
        else:
            msgs.append("NÃO OK: " + msg)
    except Exception as e:
        msgs.append(f"Não foi possível avaliar o balanço de pressão: {e}")
    return msgs
