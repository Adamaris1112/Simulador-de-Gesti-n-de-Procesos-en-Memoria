from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from typing import List, Deque, Optional
from collections import deque
import itertools
import random
import string
import time
import argparse

RAM_TOTAL_MB = 1024  

NOMBRES_BASE = [
    "Editor", "Navegador", "Compilador", "Render", "Analizador",
    "Servidor", "Cliente", "Cache", "Backup", "Indexador"
]


def nombre_aleatorio():
    base = random.choice(NOMBRES_BASE)
    suf = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"{base}-{suf}"

@dataclass
class Proceso:
    pid: int
    nombre: str
    memoria_mb: int
    duracion_s: int
    estado: str = field(default="en_cola")  # en_cola | ejecutando | terminado
    inicio_epoch: Optional[float] = field(default=None)
    fin_epoch: Optional[float] = field(default=None)

    def __post_init__(self):
     
        if self.memoria_mb <= 0:
            raise ValueError("La memoria del proceso debe ser > 0 MB")
        if self.duracion_s <= 0:
            raise ValueError("La duración del proceso debe ser > 0 segundos")

    def __str__(self):
        return (f"PID={self.pid} | {self.nombre} | Mem={self.memoria_mb}MB | "
                f"Duración={self.duracion_s}s | Estado={self.estado}")

class GestorMemoria:
    def __init__(self, ram_total_mb: int = RAM_TOTAL_MB):
        self.ram_total_mb = ram_total_mb
        self.ram_usada_mb = 0
        self.procesos_en_ejecucion: List[Proceso] = []
        self.cola_espera: Deque[Proceso] = deque()
        self._pid_counter = itertools.count(1)  

  