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


    @property
    def ram_disponible_mb(self) -> int:
        return self.ram_total_mb - self.ram_usada_mb

    def imprimir_estado(self):
        print("\n=== ESTADO DE MEMORIA ===")
        print(f"RAM Total:     {self.ram_total_mb} MB")
        print(f"RAM Usada:     {self.ram_usada_mb} MB")
        print(f"RAM Disponible:{self.ram_disponible_mb} MB")
        print("Procesos en ejecución:")
        if not self.procesos_en_ejecucion:
            print("  (ninguno)")
        else:
            for p in self.procesos_en_ejecucion:
                print(f"  - {p}")
        print("Procesos en cola:")
        if not self.cola_espera:
            print("  (ninguno)")
        else:
            for p in self.cola_espera:
                print(f"  - {p}")
        print("=========================\n")
        
#SOFAI_AND_KAREN
   
    def crear_proceso(self, nombre: Optional[str], memoria_mb: int, duracion_s: int) -> Proceso:
        pid = next(self._pid_counter)
        if not nombre or not nombre.strip():
            nombre = nombre_aleatorio()
        proc = Proceso(pid=pid, nombre=nombre.strip(), memoria_mb=memoria_mb, duracion_s=duracion_s)
        
        self.cola_espera.append(proc)
        print(f"[+] Proceso creado y enviado a cola: {proc}")
        return proc

    def _puede_iniciar(self, p: Proceso) -> bool:
        return p.memoria_mb <= self.ram_disponible_mb

    def _iniciar_proceso(self, p: Proceso):
        self.ram_usada_mb += p.memoria_mb
        p.estado = "ejecutando"
        p.inicio_epoch = time.time()
        self.procesos_en_ejecucion.append(p)
        print(f"[INICIO] {p} | RAM usada ahora: {self.ram_usada_mb} MB")

    def _finalizar_proceso(self, p: Proceso):
        self.ram_usada_mb -= p.memoria_mb
        p.estado = "terminado"
        p.fin_epoch = time.time()
        print(f"[FIN] {p} | RAM usada ahora: {self.ram_usada_mb} MB")

    async def _simular_proceso(self, p: Proceso):
        try:
            await asyncio.sleep(p.duracion_s)
        finally:
            self.procesos_en_ejecucion.remove(p)
            self._finalizar_proceso(p)
  
