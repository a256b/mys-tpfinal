class Balanza:
    def __init__(self, nombre):
        self.nombre = nombre
        self.libre = True
        self.tiempo_ocupado = 0.0
        self.ultima_asignacion = 0.0
        self.historial_ociosidad = []  # (inicio, fin, razon)

    def ocupar(self, tiempo):
        self.libre = False
        self.ultima_asignacion = tiempo
        # self.razon_ocupacion = razon

    def liberar(self, tiempo, razon="desconocido"):
        self.libre = True
        tiempo_ocupado = tiempo - self.ultima_asignacion
        self.tiempo_ocupado += tiempo_ocupado
        self.historial_ociosidad.append((self.ultima_asignacion, tiempo, razon))
