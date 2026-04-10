import pandas as pd


# =========================
# FUNÇÃO BASE
# =========================
def campo(linha, inicio, fim):
    return linha[inicio-1:fim]


# =========================
# FORMATA DATA
# =========================
def formatar_data(valor):
    if len(valor) == 8 and valor.isdigit():
        return f"{valor[6:8]}/{valor[4:6]}/{valor[0:4]}"
    return valor


# =========================
# FORMATA VALOR
# =========================
def formatar_valor(valor):
    try:
        return float(valor) / 100
    except:
        return 0


# =========================
# DETALHE CÓDIGO DE BARRAS
# =========================
def detalhar_codigo_barras(codigo):
    return (
        f"PRODUTO.............: {codigo[0]}\n"
        f"SEGMENTO............: {codigo[1]}\n"
        f"VALOR REFERÊNCIA....: {codigo[2]}\n"
        f"DV..................: {codigo[3]}\n"
        f"VALOR...............: {codigo[4:15]}\n"
        f"CODIGO FEBRABAN IPVA: {codigo[15:19]}\n"
        f"DATA VENCIMENTO.....: {formatar_data(codigo[19:27])}\n"
        f"NOSSO NUMERO.........: {codigo[27:37]}\n"
        f"CODIGO RECEITA......: {codigo[37:41]}"
    )


# =========================
# REGISTRO A (HEADER)
# =========================
def parse_linha_A(linha):
    return {
        "REGISTRO": campo(linha, 1, 1),
        "REMESSA": campo(linha, 2, 2),
        "CONVÊNIO": campo(linha, 3, 22).strip(),
        "EMPRESA": campo(linha, 23, 42).strip(),
        "BANCO": campo(linha, 43, 45),
        "NOME BANCO": campo(linha, 46, 65).strip(),
        "DATA GERAÇÃO": formatar_data(campo(linha, 66, 73)),
        "NSA": campo(linha, 74, 79),
        "VERSÃO": campo(linha, 80, 81),
        "CÓDIGO DE BARRAS": campo(linha, 82, 98),
        "FILLER": campo(linha, 99, 150)
    }


# =========================
# REGISTRO G (DETALHE)
# =========================
def parse_linha_G(linha):
    codigo_barras = campo(linha, 38, 81)

    return {
        "REGISTRO": campo(linha, 1, 1),
        "AGÊNCIA/CONTA": campo(linha, 2, 21).strip(),
        "DATA PAGAMENTO": formatar_data(campo(linha, 22, 29)),
        "DATA CRÉDITO": formatar_data(campo(linha, 30, 37)),
        "CÓDIGO DE BARRAS": detalhar_codigo_barras(codigo_barras),

        "VALOR RECEBIDO": formatar_valor(campo(linha, 82, 93)),
        "VALOR TARIFA": formatar_valor(campo(linha, 94, 100)),

        "NSR": campo(linha, 101, 108),
        "AGÊNCIA ARRECADADORA": campo(linha, 109, 116),
        "FORMA ARRECADAÇÃO": campo(linha, 117, 117),
        "AUTENTICAÇÃO": campo(linha, 118, 140).strip(),
        "FORMA PAGAMENTO": campo(linha, 141, 141),

        "FILLER": campo(linha, 142, 150),

        # 🔥 CAMPO TÉCNICO PARA FILTRO
        "CAMPO_LIVRE_FILTRO": codigo_barras[27:].strip(),
        "CODIGO_RECEITA": codigo_barras[37:41].strip()
    }


# =========================
# PROCESSAMENTO
# =========================
def processar_arquivo(caminho):
    lista_A = []
    lista_G = []

    with open(caminho, "r", encoding="latin-1") as f:
        for numero_linha, linha in enumerate(f, start=1):

            linha = linha.rstrip("\r\n")
            linha = linha.ljust(150)[:150]

            tipo = linha[0]

            if tipo == "A":
                registro = parse_linha_A(linha)
                registro["LINHA_ARQUIVO"] = numero_linha
                lista_A.append(registro)

            elif tipo == "G":
                registro = parse_linha_G(linha)
                registro["LINHA_ARQUIVO"] = numero_linha
                lista_G.append(registro)

    df_A = pd.DataFrame(lista_A)
    df_G = pd.DataFrame(lista_G)

    return df_A, df_G