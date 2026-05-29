import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_conn

CATEGORIAS = ["Aluguel", "Funcionários", "Energia", "Contas Fixas", "Outros"]

def render():
    st.header("Despesas")
    conn = get_conn()

    with st.expander("Lançar Despesa", expanded=False):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data")
        categoria = col2.selectbox("Categoria", CATEGORIAS)
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        if st.button("Salvar"):
            conn.execute(
                "INSERT INTO despesa (data, categoria, descricao, valor) VALUES (?, ?, ?, ?)",
                (str(data), categoria, descricao, valor)
            )
            conn.commit()
            st.success("Despesa salva!")
            st.rerun()

    df = pd.read_sql("SELECT * FROM despesa ORDER BY data DESC", conn)
    conn.close()

    if df.empty:
        st.info("Nenhuma despesa lançada.")
        return

    col1, col2 = st.columns(2)
    meses = sorted(df["data"].str[:7].unique(), reverse=True)
    mes = col1.selectbox("Filtrar por mês", ["Todos"] + list(meses))
    if mes != "Todos":
        df = df[df["data"].str.startswith(mes)]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Despesas", f"R$ {df['valor'].sum():,.2f}")
    col2.metric("Lançamentos", len(df))
    col3.metric("Maior Despesa", f"R$ {df['valor'].max():,.2f}")

    resumo = df.groupby("categoria")["valor"].sum().reset_index()
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.pie(resumo, names="categoria", values="valor", title="Despesas por Categoria"), use_container_width=True)
    c2.plotly_chart(px.bar(resumo, x="categoria", y="valor", title="Valor por Categoria"), use_container_width=True)

    st.dataframe(df[["data", "categoria", "descricao", "valor"]], use_container_width=True)
