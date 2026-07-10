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
.main .block-container { max-width: 95%; padding-top: 0.2rem; }
h1 { text-align: center; margin-top: -20px; margin-bottom: 5px; }
section[data-testid="stSidebar"] { width: 250px !important; }
section[data-testid="stSidebar"] input { padding: 6px !important; font-size: 13px !important; }
.header-card { background-color: #f5f7fa; padding: 6px; border-radius: 8px; text-align: center; margin-bottom: 5px; font-size: 13px; }
.topo-fixo { position: sticky; top: 0; z-index: 999; background-color: #ffffff; padding: 5px 0; border-bottom: 1px solid #ddd; }
.espaco-topo { height: 70px; }
</style>
""", unsafe_allow_html=True)


# =========================
# TÍTULO
# =========================
st.markdown("<h1>Sistema de Arrecadação</h1>", unsafe_allow_html=True)


# =========================
# SIDEBAR
# =========================
st.sidebar.title("📂 Arquivo")
arquivo = st.sidebar.file_uploader("Carregar arquivo", type=["txt"])

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

    if limpar:
        filtro = ""
        filtro_codigo_receita = ""

    # =========================
    # FILTROS
    # =========================
    if not df_filtrado.empty:
        df_filtrado["CAMPO_LIVRE_FILTRO"] = df_filtrado["CAMPO_LIVRE_FILTRO"].astype(str).str.strip()

        if filtro:
            df_filtrado = df_filtrado[df_filtrado["CAMPO_LIVRE_FILTRO"].str.startswith(filtro.strip())]

        if filtro_codigo_receita and "CODIGO_RECEITA" in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado["CODIGO_RECEITA"].astype(str).str.startswith(filtro_codigo_receita.strip())]

    # =========================
    # TOPO FIXO
    # =========================
    st.markdown('<div class="topo-fixo">', unsafe_allow_html=True)

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

    # Dashboard
    if not df_filtrado.empty and "VALOR RECEBIDO" in df_filtrado.columns:
        total_valor = df_filtrado["VALOR RECEBIDO"].sum()
        total_linhas = len(df_filtrado)
        total_valor_formatado = f"R$ {total_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        total_valor = 0
        total_linhas = 0
        total_valor_formatado = "R$ 0,00"

    col1, col2, col3 = st.columns([6, 2, 2])
    with col2: st.metric("📊 Registros", total_linhas)
    with col3: st.metric("💰 Total", total_valor_formatado)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="espaco-topo"></div>', unsafe_allow_html=True)

    # =========================
    # ORDEM DAS COLUNAS
    # =========================
    if not df_filtrado.empty:
        # Define a ordem manual desejada
        ordem_desejada = [
            "LINHA_ARQUIVO", 
            "REGISTRO", 
            "AGÊNCIA/CONTA", 
            "DATA PAGAMENTO", 
            "DATA CRÉDITO", 
            "CÓDIGO DE BARRAS", 
            "CODIGO_RECEITA", # Coluna separada
            "VALOR RECEBIDO", 
            "VALOR TARIFA", 
            "NSR", 
            "AGÊNCIA ARRECADADORA", 
            "FORMA ARRECADADA", 
            "AUTENTICAÇÃO", 
            "FORMA PAGAMENTO"
        ]
        
        # Filtra apenas colunas que existem no dataframe (caso alguma tenha mudado)
        colunas_finais = [col for col in ordem_desejada if col in df_filtrado.columns]
        
        # Adiciona colunas extras não previstas no final (se houver)
        cols_extras = [col for col in df_filtrado.columns if col not in colunas_finais and col != "CAMPO_LIVRE_FILTRO"]
        colunas_finais.extend(cols_extras)

        df_exibicao = df_filtrado[colunas_finais]
    else:
        df_exibicao = df_filtrado

    # =========================
    # DOWNLOAD
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
    # TABELA
    # =========================
    st.markdown("### 📊 Detalhes das Arrecadações")
    
    # Garante que o campo técnico não apareça
    cols_tabela = [c for c in df_exibicao.columns if c != "CAMPO_LIVRE_FILTRO"]
    
    st.dataframe(
        df_exibicao[cols_tabela],
        use_container_width=True,
        height=600
    )
else:
    st.info("👈 Carregue um arquivo .txt pela barra lateral para começar.")