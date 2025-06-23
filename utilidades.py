import numpy as np
import random

def seleccionar_tipo_camion():
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
    return np.random.exponential(scale=media)

def tiempo_pesaje():
    return max(1, np.random.normal(11, 3))

def tiempo_produccion():
    return np.random.exponential(scale=15)

def tiempo_carga(tipo):
    return {1: 23, 2: 20, 3: 28, 4: 35}[tipo]

def tiempo_viaje_cd(tipo):
    medias = {1: 29, 2: 30, 3: 35, 4: 38}
    desvios = {1: 5.1, 2: 6.4, 3: 8, 4: 12.3}
    return max(1, np.random.normal(medias[tipo], desvios[tipo]))