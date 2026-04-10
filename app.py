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
# CSS AJUSTADO
# =========================
st.markdown("""
<style>

/* CONTAINER */
.main .block-container {
    max-width: 95%;
    padding-top: 0.2rem;
}

/* TÍTULO MAIS PRA CIMA */
h1 {
    text-align: center;
    margin-top: -20px;
    margin-bottom: 5px;
}

/* SIDEBAR MAIS COMPACTA */
section[data-testid="stSidebar"] {
    width: 250px !important;
}

/* INPUTS */
section[data-testid="stSidebar"] input {
    padding: 6px !important;
    font-size: 13px !important;
}

/* HEADER */
.header-card {
    background-color: #f5f7fa;
    padding: 6px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 5px;
    font-size: 13px;
}

/* TOPO FIXO */
.topo-fixo {
    position: sticky;
    top: 0;
    z-index: 999;
    background-color: #ffffff;
    padding: 5px 0;
    border-bottom: 1px solid #ddd;
}

/* ESPAÇO */
.espaco-topo {
    height: 70px;
}

</style>
""", unsafe_allow_html=True)


# =========================
# TÍTULO
# =========================
st.markdown("<h1>Sistema de Arrecadação</h1>", unsafe_allow_html=True)


# =========================
# SIDEBAR (UPLOAD + FILTRO)
# =========================
st.sidebar.title("📂 Arquivo")

arquivo = st.sidebar.file_uploader(
    "Carregar arquivo",
    type=["txt"]
)

if arquivo:
    st.sidebar.markdown("---")
    st.sidebar.title("🔎 Filtros")

    filtro = st.sidebar.text_input("Nosso Número", placeholder="Ex: 3004")
    filtro_codigo_receita = st.sidebar.text_input("Código Receita", placeholder="Ex: 2011")

    limpar = st.sidebar.button("🧹 Limpar Filtros")
else:
    filtro = ""
    filtro_codigo_receita = ""
    limpar = False


# =========================
# PROCESSAMENTO
# =========================
if arquivo:

    with open("temp.txt", "wb") as f:
        f.write(arquivo.getbuffer())

    df_A, df_G = processar_arquivo("temp.txt")

    df_filtrado = df_G.copy()

    if limpar:
        filtro = ""
        filtro_codigo_receita = ""

    # =========================
    # FILTROS
    # =========================
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
            df_filtrado["CODIGO_RECEITA"]
            .astype(str)
            .str.startswith(filtro_codigo_receita.strip())
        ]

    # =========================
    # TOPO FIXO
    # =========================
    st.markdown('<div class="topo-fixo">', unsafe_allow_html=True)

    # HEADER
    if not df_A.empty:
        header = df_A.iloc[0]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"<div class='header-card'><b>Convênio</b><br>{header['CONVÊNIO']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='header-card'><b>Empresa</b><br>{header['EMPRESA']}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div class='header-card'><b>Banco</b><br>{header['BANCO']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='header-card'><b>Nome Banco</b><br>{header['NOME BANCO']}</div>", unsafe_allow_html=True)

        with col3:
            st.markdown(f"<div class='header-card'><b>Data Geração</b><br>{header['DATA GERAÇÃO']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='header-card'><b>NSA</b><br>{header['NSA']}</div>", unsafe_allow_html=True)

        with col4:
            st.markdown(f"<div class='header-card'><b>Versão</b><br>{header['VERSÃO']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='header-card'><b>Código de Barras</b><br>{header['CÓDIGO DE BARRAS']}</div>", unsafe_allow_html=True)

    # DASHBOARD
    total_valor = df_filtrado["VALOR RECEBIDO"].sum()
    total_linhas = len(df_filtrado)

    total_valor_formatado = f"R$ {total_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    col1, col2, col3 = st.columns([6, 2, 2])

    with col2:
        st.metric("📊 Registros", total_linhas)

    with col3:
        st.metric("💰 Total", total_valor_formatado)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="espaco-topo"></div>', unsafe_allow_html=True)

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