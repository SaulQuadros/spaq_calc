
import pandas as pd
import yaml

def load_builtin_heaters() -> pd.DataFrame:
    return pd.read_csv("src/spaq/catalog/heaters_builtin.csv")

def read_catalog_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)

def read_points_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)

def load_presets_yaml(path: str = "src/spaq/catalog/presets.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
