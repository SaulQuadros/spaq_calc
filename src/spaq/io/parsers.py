import pandas as pd

def load_builtin_heaters():
    return pd.read_csv('src/spaq/catalog/heaters_builtin.csv')

def read_catalog_csv(file):
    return pd.read_csv(file)
