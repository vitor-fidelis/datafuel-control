import streamlit as st
import pandas as pd
from database import get_conn

def importar_venda_produto(df: pd.DataFrame, data_ref: str):
    df.columns = [c.strip().upper() for c in df.columns]
    conn = get_conn()
    for _, row in df.iterrows():
        conn.execute("""
            INSERT INTO venda_produto (cod_produto, descricao, valor_unitario, quantidade, numero_serie_ecf, valor_total, data_importacao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(row.get("COD_PRODUTO", "")),
            str(row.get("DESCRICAO", "")),
            float(row.get("VALOR_UNITARIO_VENDA", 0) or 0),
            float(row.get("QUANTIDADE", 0) or 0),
            str(row.get("NUMERO_SERIE_ECF", "")),
            float(row.get("VALOR_TOTAL", 0) or 0),
            data_ref
        ))
    conn.commit()
    conn.close()

def importar_venda_diaria(df: pd.DataFrame):
    df.columns = [c.strip().upper() for c in df.columns]
    conn = get_conn()
    for _, row in df.iterrows():
        conn.execute("""
            INSERT INTO venda_diaria (data, veiculos, litragem, ticket_litragem, valor, ticket_valor)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(row.get("DATA", "")),
            int(row.get("VEICULOS", 0) or 0),
            float(row.get("LITRAGEM", 0) or 0),
            float(row.get("TICKET_LITRAGEM", 0) or 0),
            float(row.get("VALOR", 0) or 0),
            float(row.get("TICKET_VALOR", 0) or 0),
        ))
    conn.commit()
    conn.close()

def importar_venda_pagamento(df: pd.DataFrame, data_ref: str):
    df.columns = [c.strip().upper() for c in df.columns]
    conn = get_conn()
    # espera colunas: forma de pagamento como colunas, ou FORMA_PAGAMENTO + VALOR
    if "FORMA_PAGAMENTO" in df.columns and "VALOR" in df.columns:
        for _, row in df.iterrows():
            conn.execute(
                "INSERT INTO venda_pagamento (data, forma_pagamento, valor) VALUES (?, ?, ?)",
                (data_ref, str(row["FORMA_PAGAMENTO"]), float(row["VALOR"] or 0))
            )
    else:
        # formato wide: cada coluna é uma forma de pagamento
        for col in df.columns:
            total = pd.to_numeric(df[col], errors="coerce").sum()
            conn.execute(
                "INSERT INTO venda_pagamento (data, forma_pagamento, valor) VALUES (?, ?, ?)",
                (data_ref, col, float(total))
            )
    conn.commit()
    conn.close()

def render():
    st.header("Importar Dados de Vendas")

    st.subheader("Vendas por Produto")
    f1 = st.file_uploader("Arquivo xlsx — vendas por produto", type="xlsx", key="prod")
    data1 = st.date_input("Período de referência", key="data_prod")
    if f1 and st.button("Importar Produtos"):
        df = pd.read_excel(f1)
        importar_venda_produto(df, str(data1))
        st.success(f"{len(df)} registros importados.")

    st.divider()

    st.subheader("Vendas Diárias / Ticket Médio")
    f2 = st.file_uploader("Arquivo xlsx — vendas diárias", type="xlsx", key="diaria")
    if f2 and st.button("Importar Diárias"):
        df = pd.read_excel(f2)
        importar_venda_diaria(df)
        st.success(f"{len(df)} registros importados.")

    st.divider()

    st.subheader("Vendas por Forma de Pagamento")
    f3 = st.file_uploader("Arquivo xlsx — formas de pagamento", type="xlsx", key="pgto")
    data3 = st.date_input("Período de referência", key="data_pgto")
    if f3 and st.button("Importar Pagamentos"):
        df = pd.read_excel(f3)
        importar_venda_pagamento(df, str(data3))
        st.success("Importado com sucesso.")
