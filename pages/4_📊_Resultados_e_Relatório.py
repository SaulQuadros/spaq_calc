
import streamlit as st
import pandas as pd
import io, datetime

st.set_page_config(page_title="Resultados & Relatório", page_icon="📊", layout="wide")
st.title("📊 Resultados & Relatório")

res = st.session_state.get("results", None)
points = st.session_state.get("points_df", pd.DataFrame())

if not res:
    st.info("Calcule primeiro na página 🧮 Dimensionamento.")
    st.stop()

st.subheader("Resultado consolidado")
st.json(res)

st.subheader("Exportar CSV")
df_out = pd.DataFrame([res])
st.download_button("⬇️ Baixar Resultado (CSV)", data=df_out.to_csv(index=False).encode("utf-8"),
                   file_name="spaq_resultado.csv", mime="text/csv")

st.divider()
st.header("📝 Relatório PDF (padronizado)")

# Metadados do projeto
col = st.columns(3)
with col[0]:
    proj = st.text_input("Projeto", value="Dimensionamento SPAQ")
with col[1]:
    autor = st.text_input("Autor", value="")
with col[2]:
    inst = st.text_input("Instituição/Cliente", value="")

logo_path = st.text_input("Caminho do logo (PNG opcional)", value="src/spaq/report/assets/logo.png")
assinatura = st.text_area("Assinatura/Responsável Técnico (texto)",
                          value="Responsável Técnico: __________________________\nCREA/CAU: ____________")

# Referências (tabela simples)
if "references" not in st.session_state:
    st.session_state.references = [
        {"tipo":"norma","autores":"ABNT","ano":"2015","titulo":"NBR 7198 — Projeto e execução de instalações prediais de água quente","local_editora":"Rio de Janeiro: ABNT","url":"","acesso":""},
    ]
ref_df = st.data_editor(pd.DataFrame(st.session_state.references), num_rows="dynamic", use_container_width=True)
st.session_state.references = ref_df.to_dict(orient="records")

style = st.radio("Estilo de referências", ["ABNT","APA"])

def fmt_ref(ref, style):
    t = (ref.get("tipo","")).lower()
    autores = ref.get("autores","").strip()
    ano = ref.get("ano","").strip()
    titulo = ref.get("titulo","").strip()
    loced = ref.get("local_editora","").strip()
    url = ref.get("url","").strip()
    acesso = ref.get("acesso","").strip()
    if style == "ABNT":
        base = f"{autores}. {titulo}. {loced}, {ano}."
        if url:
            base += f" Disponível em: {url}."
        if acesso:
            base += f" Acesso em: {acesso}."
        return base
    else:  # APA simplificado
        base = f"{autores} ({ano}). {titulo}. {loced}."
        if url:
            base += f" {url}."
        return base

def draw_cover(c, W, H, proj, autor, inst, logo_path):
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    # Logo
    y = H - 40*mm
    try:
        c.drawImage(logo_path, 20*mm, y, width=40*mm, height=20*mm, preserveAspectRatio=True, mask='auto')
    except Exception:
        # placeholder
        c.setFillColor(colors.lightgrey); c.rect(20*mm, y, 40*mm, 20*mm, fill=1); c.setFillColor(colors.black)
        c.drawString(22*mm, y+9*mm, "LOGO")
    # Título
    c.setFont("Helvetica-Bold", 18); c.drawString(20*mm, y-10*mm, "Relatório de Dimensionamento — SPAQ")
    c.setFont("Helvetica", 12)
    c.drawString(20*mm, y-20*mm, f"Projeto: {proj}")
    c.drawString(20*mm, y-27*mm, f"Autor: {autor}")
    c.drawString(20*mm, y-34*mm, f"Instituição/Cliente: {inst}")
    c.drawString(20*mm, y-41*mm, f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}")

def draw_body(c, W, H, res, points, assinatura, refs_fmt):
    from reportlab.lib.units import mm
    c.setFont("Helvetica-Bold", 12); c.drawString(20*mm, H-25*mm, "Resumo do Dimensionamento")
    c.setFont("Helvetica", 10)
    y = H-33*mm
    for k in ["model","N_final","N_by_flow","N_by_power","q_unit_eff_lpm","power_unit_eff_kw","q_per_unit","Q_tot_lpm","dT_proj_C","power_req_kw"]:
        if k in res:
            c.drawString(20*mm, y, f"{k}: {res[k]}"); y -= 6*mm
            if y < 40*mm: c.showPage(); y = H-25*mm; c.setFont("Helvetica", 10)

    # Assinatura
    c.showPage()
    c.setFont("Helvetica-Bold", 12); c.drawString(20*mm, H-25*mm, "Assinatura")
    c.setFont("Helvetica", 10)
    y = H-35*mm
    for line in assinatura.splitlines():
        c.drawString(20*mm, y, line); y -= 6*mm

    # Referências
    c.showPage()
    c.setFont("Helvetica-Bold", 12); c.drawString(20*mm, H-25*mm, "Referências")
    c.setFont("Helvetica", 10)
    y = H-35*mm
    for r in refs_fmt:
        for line in r.split("\n"):
            c.drawString(20*mm, y, line)
            y -= 6*mm
            if y < 40*mm: c.showPage(); c.setFont("Helvetica", 10); y = H-25*mm

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    if st.button("Gerar PDF (capa, resumo, assinatura, referências)"):
        refs_fmt = [fmt_ref(r, style) for r in st.session_state.references]
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        W, H = A4
        draw_cover(c, W, H, proj, autor, inst, logo_path)
        draw_body(c, W, H, res, points, assinatura, refs_fmt)
        c.save()
        st.download_button("⬇️ Baixar PDF", data=buffer.getvalue(), file_name="spaq_relatorio_padronizado.pdf", mime="application/pdf")
except Exception as e:
    st.info(f"Para exportar PDF, instale 'reportlab'. Erro: {e}")
