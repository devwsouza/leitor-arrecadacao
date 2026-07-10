import streamlit as st
from leitor import processar_arquivo
import pandas as pd
import os

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
# SIDEBAR (UPLOAD + FILTROS)
# =========================
st.sidebar.title("📂 Arquivo")

arquivo = st.sidebar.file_uploader(
    "Carregar arquivo",
    type=["txt"]
)

# Inicializa variáveis de filtro
filtro_nosso_numero = ""
filtro_receita = ""
filtro_valor_min = None
filtro_valor_max = None
limpar = False

if arquivo:
    st.sidebar.markdown("---")
    st.sidebar.title("🔎 Filtros")

    filtro_nosso_numero = st.sidebar.text_input("Nosso Número", placeholder="Ex: 3004")
    filtro_receita = st.sidebar.text_input("Código Receita", placeholder="Ex: 2011")
    
    st.sidebar.markdown("**Faixa de Valor (R$)**")
    col_v1, col_v2 = st.sidebar.columns(2)
    with col_v1:
        val_min_str = st.text_input("Mínimo", placeholder="0.00")
    with col_v2:
        val_max_str = st.text_input("Máximo", placeholder="")
    
    # Converte valores para float se possível
    if val_min_str:
        try:
            filtro_valor_min = float(val_min_str.replace(',', '.'))
        except:
            pass
            
    if val_max_str:
        try:
            filtro_valor_max = float(val_max_str.replace(',', '.'))
        except:
            pass

    limpar = st.sidebar.button("🧹 Limpar Filtros")
    
    if limpar:
        filtro_nosso_numero = ""
        filtro_receita = ""
        filtro_valor_min = None
        filtro_valor_max = None


# =========================
# PROCESSAMENTO
# =========================
if arquivo:
    temp_path = "temp.txt"
    with open(temp_path, "wb") as f:
        f.write(arquivo.getbuffer())

    try:
        df_A, df_G = processar_arquivo(temp_path)
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
        df_A, df_G = pd.DataFrame(), pd.DataFrame()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    df_filtrado = df_G.copy()

    if not df_filtrado.empty:
        # --- APLICAÇÃO DOS FILTROS ---
        
        # 1. Filtro Nosso Número
        if filtro_nosso_numero:
            df_filtrado["CAMPO_LIVRE_FILTRO"] = df_filtrado["CAMPO_LIVRE_FILTRO"].astype(str).str.strip()
            df_filtrado = df_filtrado[
                df_filtrado["CAMPO_LIVRE_FILTRO"].str.startswith(filtro_nosso_numero.strip())
            ]

        # 2. Filtro Código Receita
        if filtro_receita:
            df_filtrado["CODIGO_RECEITA"] = df_filtrado["CODIGO_RECEITA"].astype(str).str.strip()
            df_filtrado = df_filtrado[
                df_filtrado["CODIGO_RECEITA"].str.startswith(filtro_receita.strip())
            ]

        # 3. Filtro Valor Recebido
        if filtro_valor_min is not None:
            df_filtrado = df_filtrado[df_filtrado["VALOR RECEBIDO"] >= filtro_valor_min]
            
        if filtro_valor_max is not None:
            df_filtrado = df_filtrado[df_filtrado["VALOR RECEBIDO"] <= filtro_valor_max]

    # =========================
    # TOPO FIXO (HEADER + DASHBOARD)
    # =========================
    st.markdown('<div class="topo-fixo">', unsafe_allow_html=True)

    # Header do Arquivo
    if not df_A.empty:
        header = df_A.iloc[0]
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"<div class='header-card'><b>Convênio</b><br>{header.get('CONVÊNIO', '')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='header-card'><b>Empresa</b><br>{header.get('EMPRESA', '')}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<div class='header-card'><b>Banco</b><br>{header.get('BANCO', '')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='header-card'><b>Nome Banco</b><br>{header.get('NOME BANCO', '')}</div>", unsafe_allow_html=True)

        with col3:
            st.markdown(f"<div class='header-card'><b>Data Geração</b><br>{header.get('DATA GERAÇÃO', '')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='header-card'><b>NSA</b><br>{header.get('NSA', '')}</div>", unsafe_allow_html=True)

        with col4:
            st.markdown(f"<div class='header-card'><b>Versão</b><br>{header.get('VERSÃO', '')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='header-card'><b>Cód. Barras</b><br>{header.get('CÓDIGO DE BARRAS', '')}</div>", unsafe_allow_html=True)

    # Dashboard de Totais
    total_valor = 0.0
    total_linhas = 0
    
    if not df_filtrado.empty and "VALOR RECEBIDO" in df_filtrado.columns:
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
    # ORGANIZAÇÃO DAS COLUNAS
    # =========================
    if not df_filtrado.empty:
        # Define ordem explícita: LINHA_ARQUIVO primeiro, depois o resto na ordem do DF
        cols_fixas_inicio = ["LINHA_ARQUIVO", "REGISTRO"]
        cols_excluidas = ["LINHA_ARQUIVO", "CAMPO_LIVRE_FILTRO"] # Esconde campo técnico
        
        cols_restantes = [c for c in df_filtrado.columns if c not in cols_excluidas]
        
        # Garante que as fixas venham primeiro sem duplicatas
        ordem_final = cols_fixas_inicio + [c for c in cols_restantes if c not in cols_fixas_inicio]
        
        df_exibicao = df_filtrado[ordem_final]
    else:
        df_exibicao = df_filtrado

    # =========================
    # BOTÃO DE DOWNLOAD
    # =========================
    if not df_filtrado.empty:
        csv = df_filtrado.to_csv(index=False, sep=';', decimal=',').encode('utf-8')
        st.download_button(
            label="📥 Baixar Dados Filtrados (CSV)",
            data=csv,
            file_name='arrecadacao_filtrada.csv',
            mime='text/csv',
        )

    # =========================
    # TABELA PRINCIPAL
    # =========================
    st.markdown("### 📊 Detalhes das Arrecadações")

    st.dataframe(
        df_exibicao,
        use_container_width=True,
        height=600
    )

else:
    st.info("👈 Carregue um arquivo .txt pela barra lateral para começar.")