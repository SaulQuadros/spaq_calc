import pandas as pd, math

def Q_max_prob(points_df: pd.DataFrame, K: float, weights: dict) -> float:
    if points_df.empty: return 0.0
    df = points_df.copy(); df['count']=df['count'].fillna(1).astype(float)
    total_weight = 0.0
    for _, r in df.iterrows():
        w = float(weights.get(str(r.get('kind','')).lower(), 1.0))
        total_weight += w*float(r['count'])
    return float(K)*math.sqrt(total_weight)
