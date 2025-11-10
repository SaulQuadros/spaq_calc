
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from openpyxl import load_workbook

TEMPLATE_PATH = Path("11_Dimens_SPAQ_AQ_v1.xlsx")

st.set_page_config(page_title="SPAQ/AQ -> Streamlit", layout="wide")
st.title("Conversão: Planilha → App (Streamlit)")

st.markdown("""
Este aplicativo reproduz os quadros principais da planilha **11_Dimens_SPAQ_AQ_v1.xlsx**.
- As células _azuis_ do Excel foram tratadas como **entradas do usuário**.
- As células com fórmulas foram reimplementadas em Python (pandas / numpy) e exibidas como **resultados calculados**.
- Você pode adicionar/remover linhas nas tabelas "Aparelhos com AF e AQ" e "Aparelhos só AF".
""")

def read_initial_tables(path: Path):
    if path.exists():
        try:
            wb = load_workbook(path, data_only=False)
            ws = wb.active
            t1_rows, t2_rows = [], []
            r = 3
            while r <= ws.max_row and ws.cell(row=r, column=1).value is not None:
                t1_rows.append({
                    "Aparelho": ws.cell(row=r, column=1).value,
                    "Vazão (L/min)": ws.cell(row=r, column=2).value,
                    "Pressão (m.c.a)": ws.cell(row=r, column=3).value,
                    "Quantidade": ws.cell(row=r, column=4).value,
                    "Peso": ws.cell(row=r, column=5).value
                })
                r += 1
            r = 10
            while r <= ws.max_row and ws.cell(row=r, column=1).value is not None:
                t2_rows.append({
                    "Aparelho": ws.cell(row=r, column=1).value,
                    "Vazão (L/min)": ws.cell(row=r, column=2).value,
                    "Pressão (m.c.a)": ws.cell(row=r, column=3).value,
                    "Quantidade": ws.cell(row=r, column=4).value,
                    "Peso": ws.cell(row=r, column=5).value
                })
                r += 1
            params = {k: ws[k].value for k in ["B3","B18","B19","B20","B26","B31","B32","B33","B35","C41","C42","C43"]}
            return pd.DataFrame(t1_rows), pd.DataFrame(t2_rows), params
        except Exception as e:
            st.warning(f"Erro ao ler o arquivo Excel: {e}. Usando dados padrão.")

    # Dados padrão se o arquivo não existir
    t1 = pd.DataFrame([
        {"Aparelho": "Chuveiro", "Vazão (L/min)": 12, "Pressão (m.c.a)": 4, "Quantidade": 5, "Peso": 0.4},
        {"Aparelho": "Lavatório", "Vazão (L/min)": 8, "Pressão (m.c.a)": 4, "Quantidade": 5, "Peso": 0.2},
        {"Aparelho": "Pia de cozinha", "Vazão (L/min)": 8, "Pressão (m.c.a)": 4, "Quantidade": 2, "Peso": 0.2}
    ])
    t2 = pd.DataFrame([
        {"Aparelho": "Tanque de lavar roupas", "Vazão (L/min)": 15, "Pressão (m.c.a)": 2, "Quantidade": 1, "Peso": 0.7},
        {"Aparelho": "Máquina de lavar roupas", "Vazão (L/min)": 15, "Pressão (m.c.a)": 2, "Quantidade": 1, "Peso": 0.7},
        {"Aparelho": "Vaso sanitário", "Vazão (L/min)": 8, "Pressão (m.c.a)": 2, "Quantidade": 1, "Peso": 0.5}
    ])
    params = {"B3": 12, "B18": 45, "B19": 20, "B20": 40, "B26": 0.8, "B31": 5, "B32": 6, "B33": 2, "B35": 5,
              "C41": 2, "C42": 21, "C43": 483}
    return t1, t2, params

t1_init, t2_init, params_init = read_initial_tables(TEMPLATE_PATH)

st.sidebar.header("Parâmetros gerais")
B3 = st.sidebar.number_input("B3 (chuveiros por ramal)", value=float(params_init.get("B3", 12)))
B18 = st.sidebar.number_input("B18 (Pressão disponível m.c.a)", value=float(params_init.get("B18", 45)))
B19 = st.sidebar.number_input("B19 (Pressão de consumo m.c.a)", value=float(params_init.get("B19", 20)))
B20 = st.sidebar.number_input("B20 (Perda adicional m.c.a)", value=float(params_init.get("B20", 40)))
B26 = st.sidebar.number_input("B26 (Eficiência ou divisor)", value=float(params_init.get("B26", 0.8)))
B31 = st.sidebar.number_input("B31", value=float(params_init.get("B31", 5)))
B32 = st.sidebar.number_input("B32", value=float(params_init.get("B32", 6)))
B33 = st.sidebar.number_input("B33", value=float(params_init.get("B33", 2)))
B35 = st.sidebar.number_input("B35", value=float(params_init.get("B35", 5)))

st.header("Aparelhos com AF e AQ")
t1 = st.data_editor(t1_init, num_rows="dynamic", key="t1")

st.header("Aparelhos só AF")
t2 = st.data_editor(t2_init, num_rows="dynamic", key="t2")

for df in (t1, t2):
    for col in ["Vazão (L/min)", "Pressão (m.c.a)", "Quantidade", "Peso"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

t1["Peso total"] = t1["Quantidade"] * t1["Peso"]
t2["Peso total"] = t2["Quantidade"] * t2["Peso"]

F6 = t1["Peso total"].sum()
F13 = t2["Peso total"].sum()
F7 = round(60 * (0.3 * max(F6, 0) ** 0.5), 1)
F14 = round(60 * (0.3 * max(F13, 0) ** 0.5), 1)
F15 = round(60 * (0.3 * max(F6 + F13, 0) ** 0.5) * 0.06, 1)

B21 = 1 - (B18 - B20) / (B18 - B19) if (B18 - B19) != 0 else 0
B22 = F7 * B21
B25 = B22 * (B18 - B19)
B27 = B25 / B26 if B26 != 0 else 0

B30 = t1["Pressão (m.c.a)"].max() if len(t1) else 0
B34 = B30 + B31 + B32 + B33
B36 = B35 - B34

C39 = F15
C40 = 0 if B36 > 0 else -1 * B36
C41 = st.sidebar.number_input("Aquecedor - Quantidade (C41)", value=float(params_init.get("C41", 2)))
C42 = st.sidebar.number_input("Aquecedor - Vazão (L/min) (C42)", value=float(params_init.get("C42", 21)))
C43 = st.sidebar.number_input("Aquecedor - Potência (kcal/min) (C43)", value=float(params_init.get("C43", 483)))
C44 = (C43 * C41 / (B18 - B19) / B3) if (B18 - B19) != 0 and B3 != 0 else 0

st.subheader("Resultados — Aparelhos com AF e AQ")
st.dataframe(t1.set_index("Aparelho"))
st.subheader("Resultados — Aparelhos só AF")
st.dataframe(t2.set_index("Aparelho"))

st.subheader("Cálculos Resumidos")
cols = st.columns(3)
with cols[0]:
    st.metric("Peso total AF+AQ (F6)", f"{F6:.2f}")
    st.metric("Peso total AF (F13)", f"{F13:.2f}")
with cols[1]:
    st.metric("Vazão total AF+AQ (F7)", f"{F7:.1f}")
    st.metric("Vazão total AF (F14)", f"{F14:.1f}")
with cols[2]:
    st.metric("Excedente/falta de pressão (B36)", f"{B36:.2f}")
    st.metric("Qt. Chuveiros (C44)", f"{C44:.2f}")

st.success("App carregado com sucesso! Se o Excel não estiver presente, os dados padrão foram usados.")
