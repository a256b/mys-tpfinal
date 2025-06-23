from dataclasses import dataclass
from entidades.camion import Camion

@dataclass
class Evento:
    tiempo: float
    tipo: str
    camion: Camion