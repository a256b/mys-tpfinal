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
        self.tiempo_oscioso_barraca = 0
        self.tiempo_oscioso_planta = 0
        self.ociosidad_por_falta_mp = 0
        self.ociosidad_por_falta_producto = 0
        self.camiones_en_espera_planta = 0
        self.camiones_en_espera_barraca = 0
        self.producciones_realizadas = 0
        self.dias_simulados = 0
        self.tiempo_total_simulado = 0

    def agregar_evento(self, evento):
        heapq.heappush(self.lef, (evento.tiempo, evento))

    def iniciar_simulacion(self, tiempo_simulacion):
        # aca deberia antes pesar el camion si generar_llegada_inicial() es a la planta
        # self.generar_pesaje(self.balanza_barraca)
        self.generar_llegada_barraca()
        # aca deberia antes pesar el camion si generar_llegada_inicial() es a la barraca
        while self.lef and self.tiempo_actual <= tiempo_simulacion:
            self.tiempo_actual, evento = heapq.heappop(self.lef)
            self.procesar_evento(evento)
        self.tiempo_total_simulado = tiempo_simulacion

        self.tiempo_oscioso_barraca = self.tiempo_total_simulado - self.balanza_barraca.tiempo_ocupado
        self.tiempo_oscioso_planta = self.tiempo_total_simulado - self.balanza_planta.tiempo_ocupado
        self.tiempo_oscioso_total = self.tiempo_oscioso_barraca + self.tiempo_oscioso_planta

        for inicio, fin, razon in self.balanza_planta.historial_ociosidad:
            if razon == "sin_materia_prima":
                self.ociosidad_por_falta_mp += (fin - inicio)
            elif razon == "produccion_en_curso":
                self.ociosidad_por_falta_producto += (fin - inicio)

        print(f"Osciocidad por falta de materia prima: {self.ociosidad_por_falta_mp}")
        print(f"Osciocidad por produccion en curso: {self.ociosidad_por_falta_producto}")
        print(f"Osciocidad balanza barraca: {self.tiempo_oscioso_barraca}")
        print(f"Osciocidad balanza tiempo: {self.tiempo_oscioso_planta}")
        print(f"Osciocidad total: {self.tiempo_oscioso_total}")

        self.metricas = {
            "producciones_realizadas": self.producciones_realizadas,
            "camiones_en_espera_barraca": self.camiones_en_espera_barraca,
            "camiones_en_espera_planta": self.camiones_en_espera_planta,
            "tiempo_total_simulado": self.tiempo_total_simulado,
            "tiempo_oscioso_barraca": self.tiempo_oscioso_barraca,
            "tiempo_oscioso_planta": self.tiempo_oscioso_planta,
            "tiempo_oscioso_por_falta_mp": self.ociosidad_por_falta_mp,
            "tiempo_oscioso_por_falta_producto": self.ociosidad_por_falta_producto,
            "porcentaje_osciosidad_mp": 100 * self.ociosidad_por_falta_mp / self.tiempo_oscioso_planta,
            "porcentaje_osciosidad_producto": 100 * self.ociosidad_por_falta_producto / self.tiempo_oscioso_planta,
            "tiempo_oscioso_total": self.tiempo_oscioso_total,
        }


    def generar_camion(self):
        tipo, sin_carga, maximo = util.seleccionar_tipo_camion()
        con_carga = util.pesaje_tipo_camion(tipo)
        camion = Camion(self.contador_camiones, tipo, sin_carga, maximo, con_carga)
        self.camiones.append(camion)
        self.contador_camiones += 1
        carga = con_carga - sin_carga
        self.stock_barraca -= carga


    def generar_pesaje(self, balanza, evento):

        if balanza.nombre == 'barraca':
            if self.balanza_barraca.libre:
                self.balanza_barraca.ocupar(self.tiempo_actual)
                duracion = util.tiempo_pesaje()
                self.agregar_evento(Evento(self.tiempo_actual + duracion, "fin_pesaje_barraca", evento.camion))
            else:
                self.colas_barraca.append(evento.camion)
                self.camiones_en_espera_barraca += 1

        elif balanza.nombre == 'planta':
            if self.balanza_planta.libre:
                self.balanza_planta.ocupar(self.tiempo_actual)
                duracion = util.tiempo_pesaje()
                self.agregar_evento(Evento(self.tiempo_actual + duracion, "fin_pesaje_planta", evento.camion))
            else:
                self.colas_planta.append(evento.camion)
                self.camiones_en_espera_planta += 1


    def generar_llegada_barraca(self):
        if self.contador_camiones >= self.camiones_totales:
            return 

        self.generar_camion()
        camion = self.camiones[-1]
        tiempo_llegada = util.tiempo_entre_llegadas(self.tiempo_llegadas)
        self.agregar_evento(Evento(self.tiempo_actual + tiempo_llegada, "llegada_camion_barraca", camion))


    def procesar_evento(self, evento):
        if evento.tipo == "llegada_camion_barraca":
            print(f"[{evento.tiempo:.2f}] Llegada de camión {evento.camion.id} tipo {evento.camion.tipo} a la barraca")
            self.generar_llegada_barraca()
            self.generar_pesaje(self.balanza_barraca, evento)
        
        elif evento.tipo == "llegada_camion_planta":
            print(f"[{evento.tiempo:.2f}] Llegada de camión {evento.camion.id} tipo {evento.camion.tipo} a la planta")
            self.generar_pesaje(self.balanza_planta, evento)

        elif evento.tipo == "fin_pesaje_barraca":
            print(f"[{evento.tiempo:.2f}] Fin pesaje barraca camión {evento.camion.id}")
            self.balanza_barraca.liberar(evento.tiempo, razon="camion_en_ruta_a_planta")
            tiempo_llegada_planta = util.tiempo_entre_llegadas(self.tiempo_llegadas)
            self.agregar_evento(Evento(evento.tiempo + tiempo_llegada_planta, "llegada_camion_planta", evento.camion))

            if self.colas_barraca:
                proximo = self.colas_barraca.pop(0)
                self.balanza_barraca.ocupar(evento.tiempo)
                duracion = util.tiempo_pesaje()
                self.agregar_evento(Evento(evento.tiempo + duracion, "fin_pesaje_barraca", proximo))

        elif evento.tipo == "fin_pesaje_planta":
            print(f"[{evento.tiempo:.2f}] Fin de pesaje planta camión {evento.camion.id}")
            razon = "sin_materia_prima" if self.stock_planta < 1 else "produccion_en_curso"
            self.balanza_planta.liberar(evento.tiempo, razon=razon)

            # Descarga de materia prima y producción 
            carga = evento.camion.peso_con_carga - evento.camion.peso_sin_carga 
            self.stock_planta += carga
            if self.stock_planta >= 1:
                self.producciones_realizadas += 1
                tiempo_prod = util.tiempo_produccion()
                self.agregar_evento(Evento(evento.tiempo + tiempo_prod, "fin_produccion", evento.camion))

            if self.colas_planta:
                proximo = self.colas_planta.pop(0)
                self.balanza_planta.ocupar(evento.tiempo)
                duracion = util.tiempo_pesaje()
                self.agregar_evento(Evento(evento.tiempo + duracion, "fin_pesaje_planta", proximo))

        elif evento.tipo == "fin_produccion":
            print(f"[{evento.tiempo:.2f}] Fin de producción {evento.camion.id}")
            # Simular el pesaje a la hora de irse de la planta y su positerior arribo al centro de produccion
            if self.balanza_planta.libre:
                self.balanza_planta.ocupar(self.tiempo_actual)
                duracion = util.tiempo_pesaje()
                self.agregar_evento(Evento(self.tiempo_actual + duracion, "fin_pesaje_producto", evento.camion))
            else:
                self.colas_planta.append(evento.camion)
                self.camiones_en_espera_planta += 1

        elif evento.tipo == "fin_pesaje_producto":
            print(f"[{evento.tiempo:.2f}] Fin pesaje de producto {evento.camion.id}")
            self.balanza_planta.liberar(evento.tiempo, razon="producto_listo_para_envio")
            tiempo_viaje = util.tiempo_viaje_cd(evento.camion.tipo)
            self.agregar_evento(Evento(evento.tiempo + tiempo_viaje, "verificar_stock_barraca", evento.camion))

            if self.colas_planta:
                proximo = self.colas_planta.pop(0)
                self.balanza_planta.ocupar(evento.tiempo)
                duracion = util.tiempo_pesaje()
                self.agregar_evento(Evento(evento.tiempo + duracion, "fin_pesaje_planta", proximo))

        elif evento.tipo == "verificar_stock_barraca":
            print(f"[{evento.tiempo:.2f}] Verifiacion del stock de la barraca {evento.camion.id}")

            # Descarga de materia prima y producción 
            if self.stock_barraca <= 8000:
                evento.camion.peso_con_carga = util.pesaje_tipo_camion(evento.camion.tipo)
                tiempo_reabastecimiento = util.tiempo_carga(evento.camion.tipo)
                self.agregar_evento(Evento(evento.tiempo + tiempo_reabastecimiento, "llegada_camion_barraca", evento.camion))
            else: 
                tiempo_llegada_barraca = util.tiempo_entre_llegadas(self.tiempo_llegadas)
                self.agregar_evento(Evento(evento.tiempo + tiempo_llegada_barraca, "llegada_camion_barraca", evento.camion))
                