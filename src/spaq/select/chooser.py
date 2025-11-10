import math

def choose_units(Q_tot_lpm, dT_C, q_unit_eff_lpm, p_unit_eff_kw, margin=0.0):
    N_by_flow = max(1, math.ceil(float(Q_tot_lpm)/max(1e-9, float(q_unit_eff_lpm))))
    P_req_kw = 0.0697*float(Q_tot_lpm)*float(dT_C)
    N_by_power = max(1, math.ceil(P_req_kw/max(1e-9, float(p_unit_eff_kw))))
    N_final = max(N_by_flow, N_by_power)
    q_per_unit = float(Q_tot_lpm)/float(N_final)
    return N_by_flow, N_by_power, N_final, q_per_unit
