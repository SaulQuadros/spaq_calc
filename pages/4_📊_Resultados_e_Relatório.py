
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
st.header("📝 Relatório PDF (capa institucional e rodapé normatizado)")

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
norm_text = st.text_input("Rodapé normatizado", value="Conforme diretrizes ABNT NBR 7198:2015 — Instalações Prediais de Água Quente.")
style_color = st.color_picker("Cor institucional (hex)", value="#0ea5e9")

# Referências
def fmt_ref(ref, style):
    autores = ref.get("autores","").strip()
    ano = ref.get("ano","").strip()
    titulo = ref.get("titulo","").strip()
    loced = ref.get("local_editora","").strip()
    url = ref.get("url","").strip()
    acesso = ref.get("acesso","").strip()
    if style == "ABNT":
        base = f"{autores}. {titulo}. {loced}, {ano}."
        if url: base += f" Disponível em: {url}."
        if acesso: base += f" Acesso em: {acesso}."
        return base
    else:
        base = f"{autores} ({ano}). {titulo}. {loced}."
        if url: base += f" {url}."
        return base

if "references" not in st.session_state:
    st.session_state.references = [
        {"tipo":"norma","autores":"ABNT","ano":"2015","titulo":"NBR 7198 — Projeto e execução de instalações prediais de água quente","local_editora":"Rio de Janeiro: ABNT","url":"","acesso":""},
    ]
ref_df = st.data_editor(pd.DataFrame(st.session_state.references), num_rows="dynamic", use_container_width=True)
st.session_state.references = ref_df.to_dict(orient="records")
style = st.radio("Estilo de referências", ["ABNT","APA"])

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.lib import colors

    def draw_header(c, W, H, color_hex, text_right):
        c.setFillColor(colors.HexColor(color_hex))
        c.rect(0, H-12*mm, W, 12*mm, fill=1, stroke=0)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 10)
        c.drawRightString(W-10*mm, H-8*mm, text_right)

    def draw_footer(c, W, H, color_hex, norm_text, page_num):
        c.setFillColor(colors.HexColor(color_hex))
        c.rect(0, 0, W, 10*mm, fill=1, stroke=0)
        c.setFillColor(colors.white); c.setFont("Helvetica", 9)
        c.drawString(10*mm, 4*mm, norm_text)
        c.drawRightString(W-10*mm, 4*mm, f"p. {page_num}")

    def draw_cover(c, W, H, proj, autor, inst, logo_path, color_hex):
        c.setFillColor(colors.HexColor(color_hex)); c.rect(0, H-35*mm, W, 35*mm, fill=1, stroke=0)
        try:
            c.drawImage(logo_path, 15*mm, H-30*mm, width=40*mm, height=20*mm, preserveAspectRatio=True, mask='auto')
        except Exception:
            c.setFillColor(colors.white); c.rect(15*mm, H-30*mm, 40*mm, 20*mm, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 20); c.drawString(20*mm, H-50*mm, "Relatório de Dimensionamento — SPAQ")
        c.setFont("Helvetica", 12)
        c.drawString(20*mm, H-60*mm, f"Projeto: {proj}")
        c.drawString(20*mm, H-68*mm, f"Autor: {autor}")
        c.drawString(20*mm, H-76*mm, f"Instituição/Cliente: {inst}")
        c.drawString(20*mm, H-84*mm, f"Data: {datetime.datetime.now().strftime('%d/%m/%Y')}")

    def draw_body(c, W, H, res, refs_fmt, assinatura, color_hex, norm_text):
        page = 1
        # Resumo
        draw_header(c, W, H, color_hex, "Relatório SPAQ — Resumo")
        y = H-20*mm
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12); c.drawString(15*mm, y, "Resumo do Dimensionamento"); y -= 8*mm
        c.setFont("Helvetica", 10)
        for k in ["model","N_final","N_by_flow","N_by_power","q_unit_eff_lpm","power_unit_eff_kw","q_per_unit","Q_tot_lpm","dT_proj_C","power_req_kw"]:
            if k in res:
                c.drawString(15*mm, y, f"{k}: {res[k]}"); y -= 6*mm
        draw_footer(c, W, H, color_hex, norm_text, page); c.showPage()

        # Assinatura
        page += 1
        draw_header(c, W, H, color_hex, "Relatório SPAQ — Assinatura")
        c.setFont("Helvetica-Bold", 12); c.drawString(15*mm, H-20*mm, "Assinatura / Responsável Técnico")
        c.setFont("Helvetica", 10)
        y = H-30*mm
        for line in assinatura.splitlines():
            c.drawString(15*mm, y, line); y -= 6*mm
        draw_footer(c, W, H, color_hex, norm_text, page); c.showPage()

        # Referências
        page += 1
        draw_header(c, W, H, color_hex, "Relatório SPAQ — Referências")
        c.setFont("Helvetica-Bold", 12); c.drawString(15*mm, H-20*mm, "Referências")
        c.setFont("Helvetica", 10)
        y = H-30*mm
        for r in refs_fmt:
            for line in r.split("\n"):
                c.drawString(15*mm, y, line)
                y -= 6*mm
                if y < 18*mm:
                    draw_footer(c, W, H, color_hex, norm_text, page); c.showPage(); page += 1
                    draw_header(c, W, H, color_hex, "Relatório SPAQ — Referências")
                    c.setFont("Helvetica", 10); y = H-20*mm
        draw_footer(c, W, H, color_hex, norm_text, page)

    if st.button("Gerar PDF (capa, cabeçalho/rodapé normatizado)"):
        refs_fmt = [fmt_ref(r, style) for r in st.session_state.references]
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        W, H = A4
        draw_cover(c, W, H, proj, autor, inst, logo_path, style_color); c.showPage()
        draw_body(c, W, H, res, refs_fmt, assinatura, style_color, norm_text)
        c.save()
        st.download_button("⬇️ Baixar PDF", data=buffer.getvalue(), file_name="spaq_relatorio_padronizado.pdf", mime="application/pdf")
except Exception as e:
    st.info(f"Para exportar PDF, instale 'reportlab'. Erro: {e}")
