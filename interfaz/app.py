import streamlit as st
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

# Agregar el path al directorio raíz si es necesario
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulacion import Simulador

st.set_page_config(page_title="Simulación Textil", layout="wide")
st.title("🧵 Simulación de Fábrica Textil")
st.markdown("Ajustá los parámetros y ejecutá la simulación para observar el comportamiento de la fábrica.")

st.sidebar.header("⚙️ Parámetros de Simulación")

# Parámetros del sistema
tiempo_llegadas = st.sidebar.slider("Tiempo medio entre llegadas (min)", 5, 60, 16)
stock_planta_ini = st.sidebar.slider("Stock inicial en planta (ton)", 1000, 100000, 10000)
stock_barraca_ini = st.sidebar.slider("Stock inicial en barraca (ton)", 1000, 100000, 20000)
camiones_totales = st.sidebar.slider("Cantidad total de camiones", 5, 50, 15)
horas_jornada = st.sidebar.slider("Duración de la jornada (horas)", 8, 24, 15)
dias_simulacion = st.sidebar.slider("Cantidad de días a simular", 1, 365, 1)

# Ejecutar simulación
if st.button("🚛 Ejecutar simulación"):
    minutos_totales = horas_jornada * 60 * dias_simulacion
    sim = Simulador(
        tiempo_llegadas=tiempo_llegadas,
        stock_planta_ini=stock_planta_ini,
        stock_barraca_ini=stock_barraca_ini,
        camiones_totales=camiones_totales
    )
    sim.iniciar_simulacion(minutos_totales)

    st.success("✅ Simulación completada")

    # Panel de resumen
    col1, col2, col3 = st.columns(3)
    col1.metric("⏱ Tiempo simulado", f"{minutos_totales} min")
    col2.metric("🚚 Producciones realizadas", sim.metricas["producciones_realizadas"])
    col3.metric("📦 Stock final en planta", f"{sim.stock_planta:.2f} ton")

    col4, col5, col6 = st.columns(3)
    col4.metric("🕓 Ocupación balanza planta", f"{(sim.balanza_planta.tiempo_ocupado / sim.tiempo_total_simulado) * 100:.2f}%")
    col5.metric("🕓 Ocupación balanza barraca", f"{(sim.balanza_barraca.tiempo_ocupado / sim.tiempo_total_simulado) * 100:.2f}%")
    col6.metric("🔁 Camiones esperando planta", sim.metricas["camiones_en_espera_planta"])

    col7, col8 = st.columns(2)
    col7.metric("🔁 Camiones esperando barraca", sim.metricas["camiones_en_espera_barraca"])
    col8.metric("💼 Total de camiones simulados", len(sim.camiones))

    # Preparar datos para gráficos
    falta_mp = sim.metricas["tiempo_oscioso_por_falta_mp"]
    falta_prod = sim.metricas["tiempo_oscioso_por_falta_producto"]
    total_oscioso = sim.metricas["tiempo_oscioso_planta"]

    otro = total_oscioso - (falta_mp + falta_prod)
    otro = max(0, otro)  # evitar valores negativos

    valores = [falta_mp, falta_prod, otro]
    labels = ["Ociosidad por falta MP", "Ociosidad por producción", "Otra ociosidad"]

    total = sum(valores)
    if total == 0:
        valores = [1, 0, 0]

    # Gráficos
    fig, ax = plt.subplots()
    ax.bar(labels, valores, color=["#f44336", "#ff9800", "#9e9e9e"])
    ax.set_ylabel("Minutos")
    ax.set_title("Ociosidad en balanza de planta")

    fig2, ax2 = plt.subplots()
    ax2.pie(valores, labels=labels, autopct='%1.1f%%', colors=["#f44336", "#ff9800", "#9e9e9e"])
    ax2.axis("equal")

    with st.expander("📊 Ver gráficos de resultados"):
        st.pyplot(fig)
        st.pyplot(fig2)

        st.subheader("📋 Resultados detallados")
        for key, value in sim.metricas.items():
            st.write(f"**{key.replace('_', ' ').capitalize()}:**", round(value, 2) if isinstance(value, float) else value)
