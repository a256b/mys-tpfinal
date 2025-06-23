import streamlit as st
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

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
    col2.metric("🚚 Producciones realizadas", sim.producciones_realizadas)
    col3.metric("📦 Stock final en planta", f"{sim.stock_planta:.2f} ton")

    col4, col5, col6 = st.columns(3)
    col4.metric("🕓 Ocupación balanza planta", f"{(sim.balanza_planta.tiempo_ocupado / sim.tiempo_total_simulado) * 100:.2f}%")
    col5.metric("🕓 Ocupación balanza barraca", f"{(sim.balanza_barraca.tiempo_ocupado / sim.tiempo_total_simulado) * 100:.2f}%")
    col6.metric("🔁 Camiones en cola", sim.camiones_en_espera)

    col7, col8 = st.columns(2)
    col7.metric("⚠️ % Tiempo sin stock", f"{(sim.tiempo_sin_stock / sim.tiempo_total_simulado) * 100:.2f}%")
    col8.metric("💼 Total de camiones simulados", len(sim.camiones))

    # Gráficos
    labels = ["Ocup. balanza planta", "Ocup. balanza barraca", "% Tiempo sin stock"]
    valores = [
        (sim.balanza_planta.tiempo_ocupado / sim.tiempo_total_simulado) * 100,
        (sim.balanza_barraca.tiempo_ocupado / sim.tiempo_total_simulado) * 100,
        (sim.tiempo_sin_stock / sim.tiempo_total_simulado) * 100
    ]

    fig, ax = plt.subplots()
    ax.bar(labels, valores, color=["#4caf50", "#2196f3", "#f44336"])
    ax.set_ylabel("% del tiempo")
    ax.set_title("Distribución de ocupación y pérdidas")
    ax.set_ylim(0, 100)

    fig2, ax2 = plt.subplots()
    ax2.pie(valores, labels=labels, autopct='%1.1f%%', colors=["#4caf50", "#2196f3", "#f44336"])
    ax2.axis("equal")

    with st.expander("Ver gráficos de resultados"):
        st.pyplot(fig)
        st.pyplot(fig2)

        st.subheader("Resultados de la simulación")
        metricas = sim.metricas  # atributo diccionario

        st.write("⏱️ Tiempo total simulado:", metricas['tiempo_total_simulado'], "minutos")
        st.write("🏭 Producciones realizadas:", metricas['producciones_realizadas'])
        st.write("⚠️ Tiempo sin stock (conteo):", metricas['tiempo_sin_stock'])
        st.write("🔁 Camiones en cola:", metricas['camiones_en_espera'])
        st.write("🚚 Camiones pesados:", metricas['camiones_pesados'])
        st.write("📊 Uso de balanza planta:", round((metricas['balanza_planta_ocupada'] / metricas['tiempo_total_simulado']) * 100, 2), "%")
        st.write("📊 Uso de balanza barraca:", round((metricas['balanza_barraca_ocupada'] / metricas['tiempo_total_simulado']) * 100, 2), "%")

        st.subheader("📈 Producción esperada vs. real")
        produccion_posible = metricas['tiempo_total_simulado'] // 15  # asumí 15 minutos por ciclo
        produccion_real = metricas['producciones_realizadas']
        faltante = produccion_posible - produccion_real

        st.bar_chart(pd.DataFrame({
            "Ciclos": [produccion_real, max(faltante, 0)]
        }, index=["Realizados", "Perdidos"]))
