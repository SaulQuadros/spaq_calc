
import math

G = 9.80665

# Tabela simples de rugosidade absoluta (m)
ROUGHNESS = {
    "cobre": 0.0000015,
    "aço galvanizado": 0.00015,
    "PVC": 0.0000015,
    "CPVC": 0.000003,
    "PEX": 0.000007,
    "ferro fundido": 0.00026,
}

def water_props(temp_C: float = 40.0):
    """Aproximações: densidade e viscosidade dinâmica da água em função de T.
    - rho ~ 992 kg/m³ @ 40°C
    - mu  ~ 0.653 mPa·s @ 40°C  (0.000653 Pa·s)
    """
    # Aproximações suaves
    if temp_C <= 10: rho, mu = 999.7, 0.001307
    elif temp_C <= 20: rho, mu = 998.2, 0.001002
    elif temp_C <= 30: rho, mu = 995.7, 0.000798
    elif temp_C <= 40: rho, mu = 992.2, 0.000653
    elif temp_C <= 50: rho, mu = 988.1, 0.000547
    else: rho, mu = 983.2, 0.000466
    return rho, mu

def reynolds(rho, v, D, mu):
    return (rho * v * D) / max(1e-9, mu)

def swamee_jain_f(epsilon, D, Re):
    if Re < 2300:
        # Laminar
        return 64.0 / max(1e-9, Re)
    # Turbulento (Swamee-Jain)
    term = (epsilon / max(1e-9, (3.7*D))) + (5.74 / (max(1e-9, Re)**0.9))
    return 0.25 / (math.log10(term)**2)

def velocity(Q_lps, D_m):
    A = math.pi * (D_m**2) / 4.0
    return (Q_lps) / max(1e-12, A)

def dp_darcy_weissbach(Q_lpm, L_m, D_mm, material="PVC", temp_C=40.0):
    D = float(D_mm)/1000.0
    Q_lps = float(Q_lpm)/60.0
    v = velocity(Q_lps, D)
    rho, mu = water_props(temp_C)
    Re = reynolds(rho, v, D, mu)
    eps = ROUGHNESS.get(material.lower(), 0.000003)
    f = swamee_jain_f(eps, D, Re)
    hf = f * (L_m/max(1e-9, D)) * (v*v/(2*G))   # perda de carga (m.c.a.)
    dp_kpa = rho * G * hf / 1000.0              # Pa → kPa
    return dp_kpa, {"Re": Re, "f": f, "v": v, "rho": rho, "mu": mu}

def dp_minors(Q_lpm, D_mm, K_sum, temp_C=40.0):
    D = float(D_mm)/1000.0
    Q_lps = float(Q_lpm)/60.0
    v = velocity(Q_lps, D)
    rho, mu = water_props(temp_C)
    hm = (K_sum) * (v*v/(2*G))
    dp_kpa = rho * G * hm / 1000.0
    return dp_kpa
