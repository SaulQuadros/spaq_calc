def dT_proj(T_in_C, T_set_C):
    return float(T_set_C) - float(T_in_C)

def power_from_Q_dT(Q_lpm, dT_C):
    return 0.0697*float(Q_lpm)*float(dT_C)

def q_unit_eff(Q_ref_lpm, dT_ref_C, dT_proj_C, derate=1.0):
    if dT_proj_C<=0: return 0.0
    return float(Q_ref_lpm)*(float(dT_ref_C)/float(dT_proj_C))*float(derate)

def power_unit_eff(P_nom_kw, derate=1.0):
    return float(P_nom_kw)*float(derate)
