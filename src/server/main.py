import asyncio
import multiprocessing
import threading
import queue
import sys
import time

# Importaciones
from gateway_async import iniciar_gateway
from workers_hilos import iniciar_worker
from notificador_ipc import iniciar_notificador


async def main():
    print("Iniciando Sistema Distribuido HorseWatch...\n")

    # 1. Crear los mecanismos de sincronización y comunicación
    cola_ipc = multiprocessing.Queue()
    cola_tareas = queue.Queue()        
    lock_db = threading.Lock()         
    
    # NUEVO: Memoria compartida y su Lock para que los hilos no choquen
    historial_caballos = {}
    lock_memoria = threading.Lock() 

    # 2. Levantar el Proceso Notificador (Multiprocessing)
    p_notificador = multiprocessing.Process(target=iniciar_notificador, args=(cola_ipc,))
    p_notificador.daemon = True 
    p_notificador.start()

    # 3. Levantar el Pool de Hilos (Threads Workers)
    num_hilos = 3  
    for i in range(num_hilos):
        # Le pasamos el historial y el lock de memoria a cada hilo
        t = threading.Thread(target=iniciar_worker, args=(i+1, cola_tareas, cola_ipc, lock_db, historial_caballos, lock_memoria)) # <--- CAMBIADO A iniciar_worker
        t.daemon = True
        t.start()

    # 4. Iniciar el Servidor de Sockets (AsyncIO)
    host = "127.0.0.1"
    port = 8888
    
    # El gateway se queda corriendo infinitamente
    await iniciar_gateway(host, port, cola_tareas)

if __name__ == '__main__':
    try:
        # Arranca el bucle de eventos asincrónico
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Main] Apagando el servidor HorseWatch...")
        sys.exit(0)