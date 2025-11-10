# App Dimensionamento SPAQ

Aplicativo interativo em Python + Streamlit baseado na planilha **11_Dimens_SPAQ_AQ_v1.xlsx**.

## 📋 Funcionalidades
- Dois quadros principais:
  - Aparelhos com AF e AQ  
  - Aparelhos só AF  
- Células de entrada (azuis no Excel) são editáveis pelo usuário.  
- Cálculos automáticos reproduzindo as fórmulas do Excel.  
- Adição e remoção dinâmica de linhas.  
- Resultados calculados em tempo real na tela.  
- Possibilidade de baixar o arquivo Excel com os resultados atualizados.

## 🚀 Executar localmente

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## ☁️ Publicar no Streamlit Cloud

1. Crie um repositório no GitHub (por exemplo `dimens_spaq_app`).
2. Envie os quatro arquivos:
   - `streamlit_app.py`
   - `11_Dimens_SPAQ_AQ_v1.xlsx`
   - `requirements.txt`
   - `README.md`
3. Vá até [https://streamlit.io/cloud](https://streamlit.io/cloud) → “**New app**”.
4. Conecte sua conta do GitHub.
5. Escolha o repositório e o arquivo principal `streamlit_app.py`.
6. Clique em **Deploy**.

O app ficará disponível em algo como:

```
https://dimens-spaq-app-seunome.streamlit.app
```
