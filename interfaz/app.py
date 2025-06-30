import streamlit as st
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

# Agregar el path al directorio raíz si es necesario
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulacion import Simulador

st.set_page_config(page_title="Simulación Textil", layout="wide")
st.title("🏭 Simulación de Fábrica Textil")
st.markdown("Ajustá los parámetros y ejecutá la simulación para observar el comportamiento de la fábrica.")

# Sidebar con parámetros
st.sidebar.header("⚙️ Parámetros de Simulación")

tiempo_llegadas = st.sidebar.slider(
    "Tiempo medio entre llegadas (min)", 
    5, 60, 16,
    help="Tiempo promedio entre llegadas de camiones a la planta"
)

stock_planta_ini = st.sidebar.slider(
    "Stock inicial en planta (ton)", 
    0, 20000, 10000,
    help="Cantidad inicial de materia prima en la planta"
)

stock_barraca_ini = st.sidebar.slider(
    "Stock inicial en barraca (ton)", 
    1000, 20000, 20000,
    help="Cantidad inicial de materia prima en la barraca (máx: 20000)"
)

camiones_totales = st.sidebar.slider(
    "Cantidad total de camiones", 
    5, 30, 15,
    help="Número de camiones en la flota"
)

dias_simulacion = st.sidebar.slider(
    "Cantidad de días a simular", 
    1, 30, 1,
    help="Cada día tiene 15 horas de operación (5am-8pm)"
)

# Botón de simulación
if st.button("🚀 Ejecutar simulación", type="primary"):
    # Calcular minutos totales (15 horas por día)
    minutos_totales = 15 * 60 * dias_simulacion
    
    # Crear barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Ejecutar simulación
    with st.spinner('Ejecutando simulación...'):
        sim = Simulador(
            tiempo_llegadas=tiempo_llegadas,
            stock_planta_ini=stock_planta_ini,
            stock_barraca_ini=stock_barraca_ini,
            camiones_totales=camiones_totales
        )
        sim.iniciar_simulacion(minutos_totales)
        progress_bar.progress(100)
    
    st.success("✅ Simulación completada")
    
    # Tabs para organizar resultados
    tab1, tab2, tab3 = st.tabs(["📊 Métricas Principales", "📈 Análisis de Ociosidad", "📋 Detalles"])
    
    with tab1:
        # Métricas principales en columnas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "⏱️ Tiempo simulado", 
                f"{dias_simulacion} días"
            )
            st.metric(
                "📦 Producciones realizadas", 
                sim.metricas["producciones_realizadas"],
            )
        
        with col2:
            ocupacion_planta = (sim.balanza_planta.tiempo_ocupado / sim.tiempo_total_simulado) * 100
            st.metric(
                "⚖️ Uso balanza planta", 
                f"{ocupacion_planta:.1f}%",
            )
            ocupacion_barraca = (sim.balanza_barraca.tiempo_ocupado / sim.tiempo_total_simulado) * 100
            st.metric(
                "⚖️ Uso balanza barraca", 
                f"{ocupacion_barraca:.1f}%"
            )
        
        with col3:
            st.metric("📦 Stock final planta", f"{sim.stock_planta:.0f} ton")
            st.metric("🏭 Stock final barraca", f"{sim.stock_barraca:.0f} ton")
        
        with col4:
            st.metric("🚛 Camiones en espera (planta)", sim.metricas["camiones_en_espera_planta"])
            st.metric("🚛 Camiones en espera (barraca)", sim.metricas["camiones_en_espera_barraca"])
    
    with tab2:
        st.subheader("Análisis de Tiempo Ocioso")
        
        # Preparar datos para gráficos
        tiempo_sin_mp = sim.metricas["tiempo_oscioso_por_falta_mp"]
        tiempo_otros = max(0, sim.metricas["tiempo_oscioso_planta"] - tiempo_sin_mp)
        tiempo_productivo_planta = sim.balanza_planta.tiempo_ocupado
        
        # Crear gráficos
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Gráfico de torta - Uso de balanza planta
            fig1, ax1 = plt.subplots(figsize=(8, 6))
            labels = ['Tiempo productivo', 'Sin materia prima', 'Otras demoras']
            sizes = [tiempo_productivo_planta, tiempo_sin_mp, tiempo_otros]
            colors = ['#2ecc71', '#e74c3c', '#f39c12']
            
            # Filtrar valores muy pequeños
            filtered_labels = []
            filtered_sizes = []
            filtered_colors = []
            for label, size, color in zip(labels, sizes, colors):
                if size > 0.01 * sum(sizes):  # Solo mostrar si es más del 1%
                    filtered_labels.append(label)
                    filtered_sizes.append(size)
                    filtered_colors.append(color)
            
            ax1.pie(filtered_sizes, labels=filtered_labels, colors=filtered_colors, 
                   autopct='%1.1f%%', startangle=90)
            ax1.set_title('Distribución del tiempo - Balanza Planta')
            st.pyplot(fig1)

        #Datos para grafico de barras de balanza carraca
        tiempo_oscioso_barraca = sim.metricas["tiempo_oscioso_barraca"]
        tiempo_productivo_barraca = sim.balanza_barraca.tiempo_ocupado

        with col2:
            #Grafico de torta - uso de balanza en barraca
            fig3, ax3 = plt.subplots(figsize=(8,6))
            labels = ['Tiempo productivo', 'Tiempo oscioso', 'Otras demoras']
            sizes = [tiempo_productivo_barraca, tiempo_oscioso_barraca]
            colors = ['#2ecc71', '#e74c3c']

            filtered_labels = []
            filtered_sizes = []
            filtered_colors = []
            for label, size, color in zip(labels, sizes, colors):
                if size > 0.01 * sum(sizes):  # Solo mostrar si es más del 1%
                    filtered_labels.append(label)
                    filtered_sizes.append(size)
                    filtered_colors.append(color)

            ax3.pie(filtered_sizes, labels=filtered_labels, colors=filtered_colors, autopct='%1.1f%%', startangle=90)
            ax3.set_title('Distribucion del tiempo - Balanza Barraca')
            st.pyplot(fig3)

        
        with col3:
            # Gráfico de barras - Comparación de ociosidad
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            
            categorias = ['Balanza\nPlanta', 'Balanza\nBarraca']
            tiempos_uso = [
                (sim.balanza_planta.tiempo_ocupado / sim.tiempo_total_simulado) * 100,
                (sim.balanza_barraca.tiempo_ocupado / sim.tiempo_total_simulado) * 100
            ]
            tiempos_ocio = [100 - t for t in tiempos_uso]
            
            x = range(len(categorias))
            width = 0.35
            
            bars1 = ax2.bar([i - width/2 for i in x], tiempos_uso, width, 
                           label='En uso', color='#2ecc71')
            bars2 = ax2.bar([i + width/2 for i in x], tiempos_ocio, width,
                           label='Ocioso', color='#e74c3c')
            
            ax2.set_ylabel('Porcentaje (%)')
            ax2.set_title('Comparación de uso de balanzas')
            ax2.set_xticks(x)
            ax2.set_xticklabels(categorias)
            ax2.legend()
            ax2.set_ylim(0, 100)
            
            # Agregar valores en las barras
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax2.annotate(f'{height:.1f}%',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom')
            
            st.pyplot(fig2)
        
        # Métricas adicionales
        st.subheader("📊 Análisis detallado de demoras")
        
        col1, col2 = st.columns(2)
        with col1:
            if sim.metricas["tiempo_oscioso_planta"] > 0:
                porcentaje_sin_mp = (tiempo_sin_mp / sim.metricas["tiempo_oscioso_planta"]) * 100
                st.metric(
                    "Ociosidad por falta de materia prima",
                    f"{tiempo_sin_mp:.0f} min",
                )
            else:
                st.metric("Ociosidad por falta de materia prima", "0 min")
        
        with col2:
            if sim.metricas["tiempo_oscioso_planta"] > 0:
                porcentaje_otros = (tiempo_otros / sim.metricas["tiempo_oscioso_planta"]) * 100
                st.metric(
                    "Ociosidad por otras causas",
                    f"{tiempo_otros:.0f} min",
                )
            else:
                st.metric("Ociosidad por otras causas", "0 min")
    
    with tab3:
        st.subheader("📋 Resultados detallados")
        
        # Crear DataFrame con todas las métricas
        metricas_df = pd.DataFrame([
            {"Métrica": "Producciones realizadas", "Valor": sim.metricas["producciones_realizadas"], "Unidad": "unidades"},
            {"Métrica": "Tiempo total simulado", "Valor": int(sim.metricas['tiempo_total_simulado']), "Unidad": "minutos"},
            {"Métrica": "Tiempo ocioso balanza planta", "Valor": round(sim.metricas['tiempo_oscioso_planta'], 1), "Unidad": "minutos"},
            {"Métrica": "Tiempo ocioso balanza barraca", "Valor": round(sim.metricas['tiempo_oscioso_barraca'], 1), "Unidad": "minutos"},
            {"Métrica": "Tiempo sin materia prima", "Valor": round(sim.metricas['tiempo_oscioso_por_falta_mp'], 1), "Unidad": "minutos"},
            {"Métrica": "Camiones en espera (máx planta)", "Valor": sim.metricas["camiones_en_espera_planta"], "Unidad": "camiones"},
            {"Métrica": "Camiones en espera (máx barraca)", "Valor": sim.metricas["camiones_en_espera_barraca"], "Unidad": "camiones"},
            {"Métrica": "Stock final planta", "Valor": int(sim.stock_planta), "Unidad": "toneladas"},
            {"Métrica": "Stock final barraca", "Valor": int(sim.stock_barraca), "Unidad": "toneladas"},
        ])
        
        st.dataframe(metricas_df, use_container_width=True, hide_index=True)
        

# Información adicional en el sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Información del modelo")
st.sidebar.markdown("""
- **Horario**: 5:00 AM - 8:00 PM (15 horas)
- **Materia prima por ciclo**: 1 tonelada
- **Capacidad máxima barraca**: 20,000 ton
- **Umbral reposición**: 8,000 ton
""")