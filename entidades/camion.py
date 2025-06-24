from dataclasses import dataclass

@dataclass
class Camion:
    id: int
    tipo: int
    peso_sin_carga: float
    peso_max: float
    peso_con_carga: float
    # estado: str = "viajando"