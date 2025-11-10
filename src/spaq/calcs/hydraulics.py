def dp_heater_at_q(dp_curve: dict, q_lpm: float) -> float:
    if not dp_curve: return 0.0
    xs = sorted(dp_curve.keys())
    if q_lpm<=xs[0]: return dp_curve[xs[0]]
    if q_lpm>=xs[-1]: return dp_curve[xs[-1]]
    for i in range(len(xs)-1):
        x0,x1 = xs[i], xs[i+1]
        if x0<=q_lpm<=x1:
            y0,y1 = dp_curve[x0], dp_curve[x1]
            t = (q_lpm-x0)/(x1-x0)
            return y0 + t*(y1-y0)
    return 0.0
