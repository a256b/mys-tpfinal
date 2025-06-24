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
        self.stock_planta_inicial = stock_planta_ini
        self.stock_barraca_inicial = stock_barraca_ini
        self.camiones = []
        self.camiones_libres = []  # Camiones disponibles para transporte
        self.colas_planta = []
        self.colas_barraca = []
        self.contador_camiones = 0
        self.camiones_totales = camiones_totales
        self.tiempo_llegadas = tiempo_llegadas
        
        # Métricas mejoradas
        self.tiempo_sin_materia_prima = 0  # Tiempo que la planta no puede producir por falta de MP
        self.ultima_vez_sin_mp = 0
        self.planta_sin_mp = False
        
        self.camiones_en_espera_planta = 0
        self.camiones_en_espera_barraca = 0
        self.producciones_realizadas = 0
        self.producciones_en_curso = 0
        self.producto_terminado_disponible = 0  # Producto listo para cargar
        
        self.dias_simulados = 0
        self.tiempo_total_simulado = 0

    def agregar_evento(self, evento):
        heapq.heappush(self.lef, (evento.tiempo, evento))

    def iniciar_simulacion(self, tiempo_simulacion):
        self.tiempo_total_simulado = tiempo_simulacion
        
        # Crear todos los camiones al inicio
        for i in range(self.camiones_totales):
            tipo, sin_carga, maximo = util.seleccionar_tipo_camion()
            camion = Camion(i, tipo, sin_carga, maximo, sin_carga)  # Inicialmente sin carga
            self.camiones.append(camion)
            self.camiones_libres.append(camion)
        
        # Programar múltiples llegadas iniciales para distribuir mejor los camiones
        for i in range(min(3, len(self.camiones_libres))):  # Iniciar con hasta 3 camiones
            self.programar_siguiente_llegada()
        
        # Programar revisiones periódicas de camiones libres
        tiempo_revision = util.tiempo_entre_llegadas(self.tiempo_llegadas)
        self.agregar_evento(Evento(tiempo_revision, "revisar_camiones_libres", None))
        
        # Ejecutar simulación
        while self.lef and self.tiempo_actual <= tiempo_simulacion:
            self.tiempo_actual, evento = heapq.heappop(self.lef)
            
            # Verificar si la planta puede producir
            if self.stock_planta < 1 and not self.planta_sin_mp:
                self.planta_sin_mp = True
                self.ultima_vez_sin_mp = self.tiempo_actual
            elif self.stock_planta >= 1 and self.planta_sin_mp:
                self.planta_sin_mp = False
                self.tiempo_sin_materia_prima += (self.tiempo_actual - self.ultima_vez_sin_mp)
            
            self.procesar_evento(evento)
        
        # Finalizar métricas
        if self.planta_sin_mp:
            self.tiempo_sin_materia_prima += (tiempo_simulacion - self.ultima_vez_sin_mp)
        
        self.calcular_metricas_finales()

    def programar_siguiente_llegada(self):
        """Programa la siguiente llegada de un camión con materia prima"""
        if self.camiones_libres and self.stock_barraca > 0:
            camion = self.camiones_libres.pop(0)
            
            # Cargar el camión en la barraca
            tipo = camion.tipo
            peso_carga = util.pesaje_tipo_camion(tipo)
            carga_real = peso_carga - camion.peso_sin_carga
            carga_real = min(carga_real, camion.peso_max - camion.peso_sin_carga)  # No exceder peso máximo
            carga_real = min(carga_real, self.stock_barraca)  # No cargar más de lo disponible
            
            if carga_real > 0:
                camion.peso_con_carga = camion.peso_sin_carga + carga_real
                self.stock_barraca -= carga_real
                
                # Programar llegada a barraca para pesaje
                tiempo_llegada = self.tiempo_actual + util.tiempo_entre_llegadas(self.tiempo_llegadas)
                self.agregar_evento(Evento(tiempo_llegada, "llegada_camion_barraca", camion))

    def procesar_evento(self, evento):
        if evento.tipo == "llegada_camion_barraca":
            print(f"[{evento.tiempo:.2f}] Llegada de camión {evento.camion.id} tipo {evento.camion.tipo} a la barraca (carga: {evento.camion.peso_con_carga - evento.camion.peso_sin_carga:.1f} ton)")
            self.generar_pesaje(self.balanza_barraca, evento)
            
        elif evento.tipo == "llegada_camion_planta":
            print(f"[{evento.tiempo:.2f}] Llegada de camión {evento.camion.id} tipo {evento.camion.tipo} a la planta")
            self.generar_pesaje(self.balanza_planta, evento)

        elif evento.tipo == "fin_pesaje_barraca":
            print(f"[{evento.tiempo:.2f}] Fin pesaje barraca camión {evento.camion.id}")
            self.balanza_barraca.liberar(evento.tiempo)
            
            # Enviar a planta
            self.agregar_evento(Evento(evento.tiempo + 5, "llegada_camion_planta", evento.camion))
            
            # Atender siguiente en cola
            if self.colas_barraca:
                proximo = self.colas_barraca.pop(0)
                self.balanza_barraca.ocupar(evento.tiempo)
                duracion = util.tiempo_pesaje()
                self.agregar_evento(Evento(evento.tiempo + duracion, "fin_pesaje_barraca", proximo))

        elif evento.tipo == "fin_pesaje_planta":
            print(f"[{evento.tiempo:.2f}] Fin de pesaje planta camión {evento.camion.id}")
            self.balanza_planta.liberar(evento.tiempo)
            
            # Descargar materia prima
            carga = evento.camion.peso_con_carga - evento.camion.peso_sin_carga
            self.stock_planta += carga
            print(f"[{evento.tiempo:.2f}] Descargando {carga:.1f} ton. Stock planta: {self.stock_planta:.1f} ton")
            evento.camion.peso_con_carga = evento.camion.peso_sin_carga  # Vaciar camión
            
            # Programar descarga
            tiempo_descarga = util.tiempo_carga(evento.camion.tipo)
            self.agregar_evento(Evento(evento.tiempo + tiempo_descarga, "fin_descarga", evento.camion))
            
            # Iniciar producción si hay suficiente materia prima y no hay muchas en curso
            if self.stock_planta >= 1 and self.producciones_en_curso < 3:
                self.iniciar_produccion()
            
            # Atender siguiente en cola
            if self.colas_planta:
                proximo = self.colas_planta.pop(0)
                self.balanza_planta.ocupar(evento.tiempo)
                duracion = util.tiempo_pesaje()
                self.agregar_evento(Evento(evento.tiempo + duracion, "fin_pesaje_planta", proximo))

        elif evento.tipo == "fin_descarga":
            print(f"[{evento.tiempo:.2f}] Fin descarga camión {evento.camion.id}")
            
            # Si hay producto terminado, cargar el camión
            if self.producto_terminado_disponible > 0:
                # Cargar producto terminado
                capacidad_carga = evento.camion.peso_max - evento.camion.peso_sin_carga
                carga = min(capacidad_carga, self.producto_terminado_disponible)
                evento.camion.peso_con_carga = evento.camion.peso_sin_carga + carga
                self.producto_terminado_disponible -= carga
                
                tiempo_carga = util.tiempo_carga(evento.camion.tipo)
                self.agregar_evento(Evento(evento.tiempo + tiempo_carga, "fin_carga_producto", evento.camion))
            else:
                # No hay producto, volver vacío a buscar más materia prima
                # Simular un viaje corto de vuelta a barraca
                self.camiones_libres.append(evento.camion)
                self.programar_siguiente_llegada()

        elif evento.tipo == "fin_produccion":
            print(f"[{evento.tiempo:.2f}] Fin de producción")
            self.producciones_en_curso -= 1
            self.producto_terminado_disponible += 1  # 1 tonelada de producto
            
            # Continuar produciendo si hay materia prima y capacidad
            if self.stock_planta >= 1 and self.producciones_en_curso < 3:
                self.iniciar_produccion()

        elif evento.tipo == "fin_carga_producto":
            print(f"[{evento.tiempo:.2f}] Fin carga producto camión {evento.camion.id}")
            
            # Pesar antes de salir
            if self.balanza_planta.libre:
                self.balanza_planta.ocupar(self.tiempo_actual)
                duracion = util.tiempo_pesaje()
                self.agregar_evento(Evento(self.tiempo_actual + duracion, "fin_pesaje_salida", evento.camion))
            else:
                self.colas_planta.append(evento.camion)
                self.camiones_en_espera_planta += 1

        elif evento.tipo == "fin_pesaje_salida":
            print(f"[{evento.tiempo:.2f}] Fin pesaje salida camión {evento.camion.id}")
            self.balanza_planta.liberar(evento.tiempo)
            
            # Viaje al centro de distribución
            tiempo_viaje = util.tiempo_viaje_cd(evento.camion.tipo)
            self.agregar_evento(Evento(evento.tiempo + tiempo_viaje, "retorno_de_cd", evento.camion))
            
            # Atender siguiente en cola
            if self.colas_planta:
                proximo = self.colas_planta.pop(0)
                self.balanza_planta.ocupar(evento.tiempo)
                duracion = util.tiempo_pesaje()
                
                # Determinar tipo de pesaje según el peso del camión
                if proximo.peso_con_carga > proximo.peso_sin_carga:
                    tipo_evento = "fin_pesaje_salida"
                else:
                    tipo_evento = "fin_pesaje_planta"
                
                self.agregar_evento(Evento(evento.tiempo + duracion, tipo_evento, proximo))

        elif evento.tipo == "retorno_de_cd":
            print(f"[{evento.tiempo:.2f}] Retorno de CD camión {evento.camion.id}")
            evento.camion.peso_con_carga = evento.camion.peso_sin_carga  # Vaciar
            
            # Verificar si necesita reabastecer barraca
            if self.stock_barraca < 8000:
                # Reabastecer barraca (simular que trae materia prima de fuera)
                capacidad = evento.camion.peso_max - evento.camion.peso_sin_carga
                self.stock_barraca += capacidad
                print(f"[{evento.tiempo:.2f}] Reabastecimiento de barraca: +{capacidad} ton")
            
            # Volver al pool de camiones libres
            self.camiones_libres.append(evento.camion)
            
            # Intentar programar una nueva llegada inmediatamente
            self.programar_siguiente_llegada()
            
            # Programar también una llegada futura por si este camión no se puede usar ahora
            tiempo_proxima = self.tiempo_actual + util.tiempo_entre_llegadas(self.tiempo_llegadas)
            if tiempo_proxima <= self.tiempo_total_simulado:
                self.agregar_evento(Evento(tiempo_proxima, "revisar_camiones_libres", None))
            
        elif evento.tipo == "revisar_camiones_libres":
            # Evento para revisar periódicamente si hay camiones libres
            self.programar_siguiente_llegada()
            
            # Programar siguiente revisión
            tiempo_proxima = self.tiempo_actual + util.tiempo_entre_llegadas(self.tiempo_llegadas)
            if tiempo_proxima <= self.tiempo_total_simulado:
                self.agregar_evento(Evento(tiempo_proxima, "revisar_camiones_libres", None))

    def iniciar_produccion(self):
        """Inicia un ciclo de producción si hay materia prima"""
        if self.stock_planta >= 1 and self.producciones_en_curso < 5:
            self.stock_planta -= 1  # Consumir 1 tonelada
            self.producciones_en_curso += 1
            self.producciones_realizadas += 1
            tiempo_prod = util.tiempo_produccion()
            self.agregar_evento(Evento(self.tiempo_actual + tiempo_prod, "fin_produccion", None))

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

    def calcular_metricas_finales(self):
        tiempo_oscioso_barraca = self.tiempo_total_simulado - self.balanza_barraca.tiempo_ocupado
        tiempo_oscioso_planta = self.tiempo_total_simulado - self.balanza_planta.tiempo_ocupado
        
        print(f"\n=== MÉTRICAS FINALES ===")
        print(f"Tiempo sin materia prima en planta: {self.tiempo_sin_materia_prima:.2f} min")
        print(f"Tiempo oscioso balanza barraca: {tiempo_oscioso_barraca:.2f} min")
        print(f"Tiempo oscioso balanza planta: {tiempo_oscioso_planta:.2f} min")
        print(f"Producciones realizadas: {self.producciones_realizadas}")
        print(f"Materia prima consumida: {self.stock_planta_inicial - self.stock_planta + self.stock_barraca_inicial - self.stock_barraca:.1f} ton")
        print(f"Stock final planta: {self.stock_planta:.2f} ton")
        print(f"Stock final barraca: {self.stock_barraca:.2f} ton")
        print(f"Producto terminado disponible: {self.producto_terminado_disponible:.1f} ton")
        print(f"Camiones libres al final: {len(self.camiones_libres)}")
        
        self.metricas = {
            "producciones_realizadas": self.producciones_realizadas,
            "camiones_en_espera_barraca": self.camiones_en_espera_barraca,
            "camiones_en_espera_planta": self.camiones_en_espera_planta,
            "tiempo_total_simulado": self.tiempo_total_simulado,
            "tiempo_oscioso_barraca": tiempo_oscioso_barraca,
            "tiempo_oscioso_planta": tiempo_oscioso_planta,
            "tiempo_oscioso_por_falta_mp": self.tiempo_sin_materia_prima,
            "tiempo_oscioso_por_falta_producto": tiempo_oscioso_planta - self.tiempo_sin_materia_prima,
            "porcentaje_osciosidad_mp": 100 * self.tiempo_sin_materia_prima / max(1, tiempo_oscioso_planta),
            "porcentaje_osciosidad_producto": 100 * (tiempo_oscioso_planta - self.tiempo_sin_materia_prima) / max(1, tiempo_oscioso_planta),
            "tiempo_oscioso_total": tiempo_oscioso_barraca + tiempo_oscioso_planta,
        }