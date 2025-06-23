class Balanza:
    def __init__(self, nombre):
        self.nombre = nombre
        self.libre = True
        self.tiempo_ocupado = 0.0
        self.ultima_asignacion = 0.0

    def ocupar(self, tiempo):
        self.libre = False
        self.ultima_asignacion = tiempo

    def liberar(self, tiempo):
        self.libre = True
        self.tiempo_ocupado += tiempo - self.ultima_asignacion

