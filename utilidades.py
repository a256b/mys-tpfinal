import numpy as np
import random

# Tabla 1 - Tipo de camión
def seleccionar_tipo_camion():
    """Retorna (tipo, peso_sin_carga, peso_maximo)"""
    x = random.random()
    if x < 0.3:
        return 1, 31, 38
    elif x < 0.55:
        return 2, 25, 30
    elif x < 0.85:
        return 3, 37, 44
    else:
        return 4, 43, 52

def tiempo_entre_llegadas(media=16):
    """Tiempo entre llegadas de camiones (distribución exponencial)"""
    return np.random.exponential(scale=media)

def tiempo_pesaje():
    """Tiempo de pesaje en balanza (distribución normal)"""
    return max(1, np.random.normal(11, 3))

# Tabla 2 - Pesaje según tipo de camión
def pesaje_tipo_camion(tipo):
    """Genera el peso total del camión con carga según su tipo"""
    medias = {1: 34, 2: 27.5, 3: 40, 4: 49}
    desvios = {1: 6.2, 2: 4.5, 3: 2.3, 4: 1.4}
    
    # Obtener peso máximo según tipo
    pesos_max = {1: 38, 2: 30, 3: 44, 4: 52}
    
    peso = np.random.normal(medias[tipo], desvios[tipo])
    
    # Asegurar que no exceda el peso máximo del camión
    peso = min(peso, pesos_max[tipo])
    
    # Asegurar que sea al menos el peso sin carga
    pesos_sin_carga = {1: 31, 2: 25, 3: 37, 4: 43}
    peso = max(peso, pesos_sin_carga[tipo])
    
    return peso

def tiempo_produccion():
    """Tiempo de un ciclo de producción (distribución exponencial)"""
    return np.random.exponential(scale=15)

# Tabla 3 - Tiempo de carga/descarga
def tiempo_carga(tipo):
    """Tiempo de carga/descarga según tipo de camión"""
    return {1: 23, 2: 20, 3: 28, 4: 35}[tipo]

# Tabla 4 - Tiempo de viaje al centro de distribución
def tiempo_viaje_cd(tipo):
    """Tiempo de viaje ida y vuelta al centro de distribución"""
    medias = {1: 29, 2: 30, 3: 35, 4: 38}
    desvios = {1: 5.1, 2: 6.4, 3: 8, 4: 12.3}
    return max(1, np.random.normal(medias[tipo], desvios[tipo]))