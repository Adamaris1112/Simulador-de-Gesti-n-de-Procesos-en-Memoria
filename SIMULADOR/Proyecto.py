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

    async def _planificador_loop(self):
        while self.cola_espera or self.procesos_en_ejecucion:
            arrancados_en_esta_vuelta = 0
            for _ in range(len(self.cola_espera)):
                p = self.cola_espera[0]
                if self._puede_iniciar(p):
                    self.cola_espera.popleft()
                    self._iniciar_proceso(p)
                    asyncio.create_task(self._simular_proceso(p))
                    arrancados_en_esta_vuelta += 1
                else:
                    encontrado = False
                    for i in range(1, len(self.cola_espera)):
                        candidato = self.cola_espera[i]
                        if self._puede_iniciar(candidato):
                            self.cola_espera.rotate(-i)
                            self.cola_espera.popleft()
                            self._iniciar_proceso(candidato)
                            asyncio.create_task(self._simular_proceso(candidato))
                            arrancados_en_esta_vuelta += 1
                            encontrado = True
                            break
                    if not encontrado:
                        break
            self.imprimir_estado()
            if arrancados_en_esta_vuelta == 0 and self.procesos_en_ejecucion:
                await asyncio.sleep(0.5)
            elif arrancados_en_esta_vuelta == 0 and not self.procesos_en_ejecucion and self.cola_espera:
                print("[AVISO] Hay procesos en cola que nunca podrán iniciar (piden más RAM que la disponible).")
                break
        print("\n[Simulación terminada] No quedan procesos en ejecución ni en cola (o ya no pueden iniciar).\n")
    async def ejecutar(self):
        await self._planificador_loop()
def imprimir_menu():
    print("\n===== Simulador de Gestión de Procesos (RAM 1 GB) =====")
    print("1) Agregar proceso")
    print("2) Agregar varios procesos de ejemplo")
    print("3) Ver estado de memoria")
    print("4) Iniciar simulación")
    print("5) Salir")
    print("========================================================")

def pedir_int(msg: str, minimo: int = 1, maximo: Optional[int] = None) -> int:
    while True:
        try:
            val = int(input(msg).strip())
            if val < minimo or (maximo is not None and val > maximo):
                print(f"Por favor ingresa un número válido (>= {minimo}" + (f" y <= {maximo}" if maximo else "") + ").")
                continue
            return val
        except ValueError:
            print("Entrada inválida, intenta de nuevo.")

def pedir_str(msg: str) -> str:
    return input(msg).strip()

def agregar_proceso_desde_input(gm: GestorMemoria):
    print("\n--- Crear Proceso ---")
    nombre = pedir_str("Nombre (enter para generar automáticamente): ")
    memoria = pedir_int("Memoria requerida (MB): ", minimo=1)
    duracion = pedir_int("Duración (segundos): ", minimo=1)
    gm.crear_proceso(nombre or None, memoria, duracion)

def agregar_procesos_demo(gm: GestorMemoria, n: int = 5):
    print(f"\n--- Agregando {n} procesos de ejemplo ---")
    for _ in range(n):
        mem = random.choice([64, 128, 256, 512, 768, 900])
        dur = random.choice([2, 3, 4, 5, 6, 7, 8])
        gm.crear_proceso(None, mem, dur)

async def menu_interactivo():
    gm = GestorMemoria()
    while True:
        imprimir_menu()
        op = pedir_str("Elige una opción: ")
        if op == "1":
            agregar_proceso_desde_input(gm)
        elif op == "2":
            n = pedir_int("¿Cuántos procesos de ejemplo? ", minimo=1, maximo=50)
            agregar_procesos_demo(gm, n)
        elif op == "3":
            gm.imprimir_estado()
        elif op == "4":
            print("\n*** Iniciando simulación... ***")
            await gm.ejecutar()
        elif op == "5":
            print("Saliendo. ¡Gracias!😂")
            return
        else:
            print("Opción no válida. Intenta de nuevo.")
def main():
    parser = argparse.ArgumentParser(description="Simulador de Gestión de Procesos en Memoria ")
    parser.add_argument("--demo", action="store_true", help="Crea procesos de ejemplo y ejecuta la simulación automáticamente")
    args = parser.parse_args()

    if args.demo:
        gm = GestorMemoria()
        agregar_procesos_demo(gm, n=8)
        print("\n*** Iniciando simulación DEMO... ***")
        asyncio.run(gm.ejecutar())
    else:
        try:
            asyncio.run(menu_interactivo())
        except KeyboardInterrupt:
            print("\nInterrumpido por el usuario.")

if __name__ == "__main__":
    main()
    
  
