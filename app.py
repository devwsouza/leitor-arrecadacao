import streamlit as st
from leitor import processar_arquivo


# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Sistema de Arrecadação",
    layout="wide"
)


# =========================
# CSS
# =========================
st.markdown("""
<style>
.main .block-container {
    max-width: 95%;
    padding-top: 0.5rem;
}

h1 {
    text-align: center;
    margin-top: -10px;
    margin-bottom: 10px;
}

.stFileUploader {
    max-width: 500px;
    margin: 0 auto;
}

[data-testid="stDataFrame"] pre {
    white-space: pre-wrap !important;
    word-break: break-word;
}

.header-box {
    background-color: #f5f7fa;
    padding: 10px;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# TÍTULO
# =========================
st.markdown("<h1>Sistema de Arrecadação</h1>", unsafe_allow_html=True)


# =========================
# UPLOAD
# =========================
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    arquivo = st.file_uploader("", type=["txt"])


# =========================
# PROCESSAMENTO
# =========================
if arquivo:
    with open("temp.txt", "wb") as f:
        f.write(arquivo.getbuffer())

    df_A, df_G = processar_arquivo("temp.txt")

    # =========================
    # HEADER
    # =========================
    st.markdown("### 📌 Header do Arquivo")

    st.markdown('<div class="header-box">', unsafe_allow_html=True)
    st.dataframe(df_A, use_container_width=True, height=120)
    st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # FILTRO
    # =========================
    st.subheader("🔎 Filtro")

    filtro = st.text_input("Nosso Número (inicia com)", placeholder="Ex: 3004")
    filtro_codigo_receita = st.text_input("Código Receita (inicia com)")

    df_filtrado = df_G.copy()

    # limpa campo
    df_filtrado["CAMPO_LIVRE_FILTRO"] = (
        df_filtrado["CAMPO_LIVRE_FILTRO"]
        .astype(str)
        .str.strip()
    )

    if filtro:
        df_filtrado = df_filtrado[
            df_filtrado["CAMPO_LIVRE_FILTRO"]
            .str.startswith(filtro.strip())
        ]

    if filtro_codigo_receita:
       df_filtrado = df_filtrado[
            df_filtrado["CODIGO_RECEITA"].str.startswith(filtro_codigo_receita.strip())    
    ]
    # =========================
    # ORGANIZA COLUNAS
    # =========================
    colunas = ["LINHA_ARQUIVO"] + [
        col for col in df_filtrado.columns
        if col not in ["LINHA_ARQUIVO", "CAMPO_LIVRE_FILTRO"]
    ]

    df_filtrado = df_filtrado[colunas]

    # =========================
    # TABELA
    # =========================
    st.markdown("### 📊 Detalhes das Arrecadações")

    st.dataframe(
    df_filtrado.drop(
        columns=["CAMPO_LIVRE_FILTRO", "CODIGO_RECEITA"],
        errors="ignore"
    ),
    use_container_width=True,
    height=600
)