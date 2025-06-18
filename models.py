import numpy as np

TIPOS_CAMION = [
    {"tipo": 1, "peso_sc": 31, "peso_max": 38, "prob": 0.3, "media_pesaje": 34, "desvio_pesaje": 6.2, "tiempo_carga": 23},
    {"tipo": 2, "peso_sc": 25, "peso_max": 30, "prob": 0.25, "media_pesaje": 27.5, "desvio_pesaje": 4.5, "tiempo_carga": 20},
    {"tipo": 3, "peso_sc": 37, "peso_max": 44, "prob": 0.3, "media_pesaje": 40, "desvio_pesaje": 2.3, "tiempo_carga": 28},
    {"tipo": 4, "peso_sc": 43, "peso_max": 52, "prob": 0.15, "media_pesaje": 49, "desvio_pesaje": 1.4, "tiempo_carga": 35},
]

def generar_tipo_camion():
    r = np.random.rand()
    acumulada = 0
    for tipo in TIPOS_CAMION:
        acumulada += tipo["prob"]
        if r < acumulada:
            return tipo
    return TIPOS_CAMION[-1]

class Camion:
    def __init__(self, id_):
        self.id = id_
        self.tipo = generar_tipo_camion()
        self.estado = "en_viaje"
        self.peso_carga = self.generar_peso_con_carga()

    def generar_peso_con_carga(self):
        peso = np.random.normal(self.tipo["media_pesaje"], self.tipo["desvio_pesaje"])
        return min(max(0, peso), self.tipo["peso_max"])
