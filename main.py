import streamlit as st
from simulator import EstadoSistema

st.set_page_config(page_title="Simulación Fábrica Textil", layout="centered")

st.title("Simulación de una Fábrica Textil")

if st.button("Iniciar simulación"):
    sistema = EstadoSistema()
    sistema.simular()
    st.success("Simulación finalizada")

    st.subheader("Eventos registrados")
    for tiempo, tipo in sistema.eventos_log:
        st.text(f"{tiempo:.2f} min: {tipo}")
