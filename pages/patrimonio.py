import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_conn

TIPOS = ["Dinheiro em Caixa", "Saldo em Conta", "Nota a Prazo"]

def render():
    st.header("Patrimônio Operacional")
    conn = get_conn()

    with st.expander("Lançar Patrimônio", expanded=False):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data")
        tipo = col2.selectbox("Tipo", TIPOS)
        descricao = st.text_input("Descrição (opcional)")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        if st.button("Salvar"):
            conn.execute(
                "INSERT INTO patrimonio (data, tipo, descricao, valor) VALUES (?, ?, ?, ?)",
                (str(data), tipo, descricao, valor)
            )
            conn.commit()
            st.success("Registro salvo!")
            st.rerun()

    df = pd.read_sql("SELECT * FROM patrimonio ORDER BY data DESC", conn)
    conn.close()

    if df.empty:
        st.info("Nenhum registro lançado.")
        return

    ultimo = df.sort_values("data").groupby("tipo").last().reset_index()
    total = ultimo["valor"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Patrimônio Total", f"R$ {total:,.2f}")
    for i, tipo in enumerate(TIPOS):
        val = ultimo.loc[ultimo["tipo"] == tipo, "valor"].sum()
        [col2, col3, col4][i].metric(tipo, f"R$ {val:,.2f}")

    st.plotly_chart(
        px.pie(ultimo, names="tipo", values="valor", title="Composição do Patrimônio"),
        use_container_width=True
    )

    st.subheader("Histórico")
    st.dataframe(df[["data", "tipo", "descricao", "valor"]], use_container_width=True)
