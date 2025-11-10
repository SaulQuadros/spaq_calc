import pandas as pd

def Q_max_possible(points_df: pd.DataFrame) -> float:
    if points_df.empty: return 0.0
    df = points_df.copy(); df['count']=df['count'].fillna(1).astype(float); df['flow_lpm']=df['flow_lpm'].astype(float)
    return float((df['flow_lpm']*df['count']).sum())
