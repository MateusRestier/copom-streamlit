import streamlit as st

st.set_page_config(
    page_title="COPOM RAG",
    page_icon="🏦",
    layout="wide",
)

inicio = st.Page("pages/0_Inicio.py", title="Inicio", icon=":material/home:")
perguntas = st.Page("pages/1_Perguntas.py", title="Perguntas", icon=":material/chat:")
admin = st.Page("pages/2_Admin.py", title="Administracao", icon=":material/settings:")

pg = st.navigation([inicio, perguntas, admin])
pg.run()
