
import pandas as pd
import yaml
from io import StringIO, BytesIO

def load_builtin_heaters() -> pd.DataFrame:
    return pd.read_csv("src/spaq/catalog/heaters_builtin.csv")

def read_catalog_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)

def read_points_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)

def load_presets_yaml(path: str = "src/spaq/catalog/presets.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def read_dp_curves_csv(file) -> dict:
    """CSV longo: model,lpm,dp_kpa -> {model: {lpm: dp}}"""
    df = pd.read_csv(file)
    req = {"model","lpm","dp_kpa"}
    if not req.issubset(set(df.columns)):
        raise ValueError("CSV de curvas deve conter colunas: model,lpm,dp_kpa")
    curves = {}
    for m, sub in df.groupby("model"):
        curves[m] = {float(r.lpm): float(r.dp_kpa) for r in sub.itertuples(index=False)}
    return curves
