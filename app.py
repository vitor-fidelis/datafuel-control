import streamlit as st
import pandas as pd
from database import get_conn, init_db
from pages import vendas, despesas, patrimonio
from utils import importar_xlsx

init_db()

st.set_page_config(page_title="DataFuel Control", page_icon="⛽", layout="wide")
st.title("⛽ DataFuel Control")

menu = st.sidebar.radio("Menu", ["Dashboard", "Vendas", "Despesas", "Patrimônio", "Importar Dados"])

if menu == "Dashboard":
    st.header("Resumo Geral")
    conn = get_conn()

    df_venda = pd.read_sql("SELECT * FROM venda_diaria", conn)
    df_desp = pd.read_sql("SELECT * FROM despesa", conn)
    df_pat = pd.read_sql("SELECT * FROM patrimonio", conn)
    conn.close()

    faturamento = df_venda["valor"].sum() if not df_venda.empty else 0
    despesas_total = df_desp["valor"].sum() if not df_desp.empty else 0
    lucro = faturamento - despesas_total
    patrimonio_total = df_pat.sort_values("data").groupby("tipo")["valor"].last().sum() if not df_pat.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Faturamento Total", f"R$ {faturamento:,.2f}")
    col2.metric("Despesas Totais", f"R$ {despesas_total:,.2f}")
    col3.metric("Resultado", f"R$ {lucro:,.2f}", delta=f"{lucro:,.2f}")
    col4.metric("Patrimônio Operacional", f"R$ {patrimonio_total:,.2f}")

    if not df_venda.empty:
        import plotly.express as px
        st.plotly_chart(
            px.line(df_venda.sort_values("data"), x="data", y="valor", title="Faturamento Diário"),
            use_container_width=True
        )

elif menu == "Vendas":
    vendas.render()

elif menu == "Despesas":
    despesas.render()

elif menu == "Patrimônio":
    patrimonio.render()

elif menu == "Importar Dados":
    importar_xlsx.render()
