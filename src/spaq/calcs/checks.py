import pandas as pd

def check_min_flow_on(points_df: pd.DataFrame, q_min_on_lpm: float):
    msgs=[]
    for _,r in points_df.iterrows():
        if float(r['flow_lpm']) < float(q_min_on_lpm):
            msgs.append(f"{r['name']}: vazão {r['flow_lpm']} L/min < vazão mínima de acionamento ({q_min_on_lpm} L/min).")
    return msgs

def check_p_min_dyn(points_df: pd.DataFrame, p_min_dyn_kpa_model: float):
    msgs=[]
    for _,r in points_df.iterrows():
        if float(r['p_min_dyn_kpa']) < float(p_min_dyn_kpa_model):
            msgs.append(f"{r['name']}: pressão mínima no ponto {r['p_min_dyn_kpa']} kPa < exigida pelo modelo ({p_min_dyn_kpa_model} kPa).")
    return msgs
