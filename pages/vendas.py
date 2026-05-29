import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_conn

def render():
    st.header("Análise de Vendas")
    conn = get_conn()

    tab1, tab2, tab3 = st.tabs(["Por Produto", "Diária / Ticket Médio", "Forma de Pagamento"])

    with tab1:
        df = pd.read_sql("SELECT * FROM venda_produto", conn)
        if df.empty:
            st.info("Nenhum dado importado ainda.")
        else:
            datas = sorted(df["data_importacao"].unique())
            sel = st.selectbox("Período", ["Todos"] + list(datas))
            if sel != "Todos":
                df = df[df["data_importacao"] == sel]

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Vendido", f"R$ {df['valor_total'].sum():,.2f}")
            col2.metric("Qtd Itens", f"{df['quantidade'].sum():,.0f}")
            col3.metric("Produtos", df["descricao"].nunique())

            top = df.groupby("descricao")["valor_total"].sum().reset_index().sort_values("valor_total", ascending=False).head(10)
            st.plotly_chart(px.bar(top, x="descricao", y="valor_total", title="Top 10 Produtos por Valor", labels={"descricao": "Produto", "valor_total": "R$"}), use_container_width=True)
            st.dataframe(df[["cod_produto", "descricao", "valor_unitario", "quantidade", "valor_total"]], use_container_width=True)

    with tab2:
        df = pd.read_sql("SELECT * FROM venda_diaria ORDER BY data", conn)
        if df.empty:
            st.info("Nenhum dado importado ainda.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Vendido", f"R$ {df['valor'].sum():,.2f}")
            col2.metric("Total Litros", f"{df['litragem'].sum():,.2f} L")
            col3.metric("Ticket Médio (R$)", f"R$ {df['ticket_valor'].mean():,.2f}")

            st.plotly_chart(px.line(df, x="data", y="valor", title="Faturamento Diário", labels={"data": "Data", "valor": "R$"}), use_container_width=True)

            col_a, col_b = st.columns(2)
            col_a.plotly_chart(px.line(df, x="data", y="litragem", title="Litragem Diária"), use_container_width=True)
            col_b.plotly_chart(px.line(df, x="data", y="veiculos", title="Veículos Atendidos"), use_container_width=True)
            st.dataframe(df.drop(columns=["id"]), use_container_width=True)

    with tab3:
        df = pd.read_sql("SELECT * FROM venda_pagamento", conn)
        if df.empty:
            st.info("Nenhum dado importado ainda.")
        else:
            resumo = df.groupby("forma_pagamento")["valor"].sum().reset_index()
            col1, col2 = st.columns(2)
            col1.plotly_chart(px.pie(resumo, names="forma_pagamento", values="valor", title="Distribuição por Pagamento"), use_container_width=True)
            col2.plotly_chart(px.bar(resumo, x="forma_pagamento", y="valor", title="Valor por Forma de Pagamento"), use_container_width=True)
            st.dataframe(resumo, use_container_width=True)

    conn.close()
