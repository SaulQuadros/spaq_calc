
import streamlit as st
import pandas as pd
import io

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

st.subheader("Gerar PDF (experimental)")
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    if st.button("Gerar PDF"):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        W, H = A4
        x, y = 20*mm, H - 20*mm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x, y, "Relatório de Dimensionamento (SPAQ)")
        y -= 12*mm
        c.setFont("Helvetica", 10)
        for k in ["model","N_final","N_by_flow","N_by_power","q_unit_eff_lpm","power_unit_eff_kw","q_per_unit","Q_tot_lpm","dT_proj_C","power_req_kw"]:
            if k in res:
                c.drawString(x, y, f"{k}: {res[k]}")
                y -= 6*mm
                if y < 30*mm:
                    c.showPage(); y = H - 20*mm; c.setFont("Helvetica", 10)
        c.showPage()
        c.save()
        pdf_bytes = buffer.getvalue()
        st.download_button("⬇️ Baixar PDF", data=pdf_bytes, file_name="spaq_relatorio.pdf", mime="application/pdf")
except Exception as e:
    st.info(f"Para exportar PDF, instale 'reportlab'. Erro: {e}")
