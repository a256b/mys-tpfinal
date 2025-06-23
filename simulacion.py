import heapq
from recursos.balanzas import Balanza
from eventos.evento import Evento
from entidades.camion import Camion
import utilidades as util

class Simulador:
    def __init__(self, tiempo_llegadas=16, stock_planta_ini=10000, stock_barraca_ini=20000, camiones_totales=15):
        self.tiempo_actual = 0
        self.lef = []
        self.balanza_planta = Balanza("planta")
        self.balanza_barraca = Balanza("barraca")
        self.stock_planta = stock_planta_ini
        self.stock_barraca = stock_barraca_ini
        self.camiones = []
        self.colas_planta = []
        self.colas_barraca = []
        self.contador_camiones = 0
        self.camiones_totales = camiones_totales
        self.tiempo_llegadas = tiempo_llegadas
        self.tiempo_sin_stock = 0
        self.camiones_en_espera = 0
        self.camiones_pesados = 0
        self.producciones_realizadas = 0
        self.dias_simulados = 0
        self.tiempo_total_simulado = 0

    def agregar_evento(self, evento):
        heapq.heappush(self.lef, (evento.tiempo, evento))

    def iniciar_simulacion(self, tiempo_simulacion):
        self.generar_llegada_inicial()
        while self.lef and self.tiempo_actual <= tiempo_simulacion:
            self.tiempo_actual, evento = heapq.heappop(self.lef)
            self.procesar_evento(evento)
        self.tiempo_total_simulado = tiempo_simulacion

        self.metricas = {
            "producciones_realizadas": self.producciones_realizadas,
            "tiempo_sin_stock": self.tiempo_sin_stock,
            "camiones_en_espera": self.camiones_en_espera,
            "tiempo_total_simulado": self.tiempo_total_simulado,
            "camiones_pesados": self.camiones_pesados,
            "balanza_planta_ocupada": self.balanza_planta.tiempo_ocupado,
            "balanza_barraca_ocupada": self.balanza_barraca.tiempo_ocupado,
        }

    def generar_llegada_inicial(self):
        if self.contador_camiones >= self.camiones_totales:
            return

        tipo, sin_carga, maximo = util.seleccionar_tipo_camion()
        camion = Camion(self.contador_camiones, tipo, sin_carga, maximo)
        self.camiones.append(camion)
        self.contador_camiones += 1
        tiempo_llegada = util.tiempo_entre_llegadas(self.tiempo_llegadas)
        self.agregar_evento(Evento(self.tiempo_actual + tiempo_llegada, "llegada_camion", camion))

    def procesar_evento(self, evento):
        if evento.tipo == "llegada_camion":
            print(f"[{evento.tiempo:.2f}] Llegada de camión {evento.camion.id} tipo {evento.camion.tipo}")
            self.generar_llegada_inicial()

            if self.balanza_planta.libre:
                self.balanza_planta.ocupar(evento.tiempo)
                duracion = util.tiempo_pesaje()
                self.agregar_evento(Evento(evento.tiempo + duracion, "fin_pesaje", evento.camion))
            else:
                self.colas_planta.append(evento.camion)
                self.camiones_en_espera += 1

        elif evento.tipo == "fin_pesaje":
            print(f"[{evento.tiempo:.2f}] Fin de pesaje camión {evento.camion.id}")
            self.balanza_planta.liberar(evento.tiempo)

            # Descarga de materia prima y producción
            descarga = evento.camion.peso_max * 0.9
            if self.stock_planta >= descarga:
                self.stock_planta -= descarga
                self.producciones_realizadas += 1
                tiempo_prod = util.tiempo_produccion()
                self.agregar_evento(Evento(evento.tiempo + tiempo_prod, "fin_produccion", evento.camion))
            else:
                self.tiempo_sin_stock += 1  # Contador básico, puede mejorarse

            if self.colas_planta:
                proximo = self.colas_planta.pop(0)
                self.balanza_planta.ocupar(evento.tiempo)
                duracion = util.tiempo_pesaje()
                self.agregar_evento(Evento(evento.tiempo + duracion, "fin_pesaje", proximo))

        elif evento.tipo == "fin_produccion":
            print(f"[{evento.tiempo:.2f}] Fin de producción camión {evento.camion.id}")
            # Simular regreso a la barraca para reabastecer
            tiempo_viaje = util.tiempo_viaje_cd(evento.camion.tipo)
            self.agregar_evento(Evento(evento.tiempo + tiempo_viaje, "llegada_barraca", evento.camion))

        elif evento.tipo == "llegada_barraca":
            print(f"[{evento.tiempo:.2f}] Llegada a barraca camión {evento.camion.id}")
            if self.balanza_barraca.libre:
                self.balanza_barraca.ocupar(evento.tiempo)
                duracion = util.tiempo_pesaje()
                self.agregar_evento(Evento(evento.tiempo + duracion, "fin_pesaje_barraca", evento.camion))
            else:
                self.colas_barraca.append(evento.camion)

        elif evento.tipo == "fin_pesaje_barraca":
            print(f"[{evento.tiempo:.2f}] Fin pesaje barraca camión {evento.camion.id}")
            self.balanza_barraca.liberar(evento.tiempo)
            # Listo para volver a planta con carga nueva
            tiempo_retorno = util.tiempo_viaje_cd(evento.camion.tipo)
            self.agregar_evento(Evento(evento.tiempo + tiempo_retorno, "llegada_camion", evento.camion))

            if self.colas_barraca:
                proximo = self.colas_barraca.pop(0)
                self.balanza_barraca.ocupar(evento.tiempo)
                duracion = util.tiempo_pesaje()
                self.agregar_evento(Evento(evento.tiempo + duracion, "fin_pesaje_barraca", proximo))