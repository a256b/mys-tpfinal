from dataclasses import dataclass

@dataclass
class Camion:
    id: int
    tipo: int
    peso_sin_carga: float
    peso_max: float
    carga: float = 0.0
    estado: str = "viajando"