import heapq
import numpy as np
from models import Camion

class Evento:
    def __init__(self, tiempo, tipo, camion=None):
        self.tiempo = tiempo
        self.tipo = tipo
        self.camion = camion

    def __lt__(self, other):
        return self.tiempo < other.tiempo

class EstadoSistema:
    def __init__(self):
        self.tiempo = 0
        self.lef = []
        self.stock_planta = 0
        self.stock_barraca = 20000
        self.balanza_ocupada = False
        self.cola_balanza = []
        self.camiones = []
        self.eventos_log = []

    def agendar_evento(self, evento):
        heapq.heappush(self.lef, evento)

    def simular(self, tiempo_max=900):  # 900 minutos = 15 horas
        tiempo_llegada = np.random.exponential(16)
        self.agendar_evento(Evento(tiempo_llegada, "llegada_camion"))

        while self.lef and self.tiempo < tiempo_max:
            evento = heapq.heappop(self.lef)
            self.tiempo = evento.tiempo
            self.eventos_log.append((self.tiempo, evento.tipo))

            if evento.tipo == "llegada_camion":
                camion = Camion(len(self.camiones))
                self.camiones.append(camion)
                if self.balanza_ocupada:
                    self.cola_balanza.append(camion)
                else:
                    self.balanza_ocupada = True
                    duracion = max(0, np.random.normal(11, 3))
                    self.agendar_evento(Evento(self.tiempo + duracion, "fin_pesaje", camion))
                # agendar próxima llegada
                proxima = self.tiempo + np.random.exponential(16)
                if proxima < tiempo_max:
                    self.agendar_evento(Evento(proxima, "llegada_camion"))

            elif evento.tipo == "fin_pesaje":
                if self.cola_balanza:
                    siguiente = self.cola_balanza.pop(0)
                    duracion = max(0, np.random.normal(11, 3))
                    self.agendar_evento(Evento(self.tiempo + duracion, "fin_pesaje", siguiente))
                else:
                    self.balanza_ocupada = False
