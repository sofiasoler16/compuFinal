import asyncio
import json
import functools

    
    # Corrutina que maneja la conexión individual de cada sensor.
    # Es asincrónica, por lo que puede atender a miles de caballos a la vez.
    
    #No es multiprocessing porque: rear un Proceso nuevo (aislado y con su propia memoria) 
    #a nivel del sistema operativo es un recurso 'caro' y pesado. Si tuviéramos 1000 caballos 
    #conectados al mismo tiempo, la computadora intentaría levantar 1000 procesos distintos
    # y se quedaría sin memoria RAM instantáneamente.

    # No es multithreading porque: asignar un Hilo (Thread) a cada sensor también es ineficiente 
    # para tareas de red. Las conexiones de red son I/O Bound (limitadas por entrada/salida,
    # es decir, son lentas). Si un caballo tiene mala señal y tarda en dictar sus síntomas,
    # el Hilo se quedaría congelado esperando, bloqueando recursos.


async def manejar_cliente(reader, writer, cola_tareas): # Definir funcion con comportamiento async

    direccion = writer.get_extra_info('peername') # De que puerto e IP entro el nuevo sensor que lee reader
    print(f"[Gateway] Nueva conexión desde el sensor en {direccion}")

    try:
        while True:
            # await: Pone en espera para un sensor y escucha otros si ya no dice nada
            data = await reader.readline() # reader.readline(): escuchar hasta un Enter
            
            if not data:
                break # El sensor cerró la conexión

            mensaje_texto = data.decode().strip() # Deja limpio para leer. VUelve a JSON
            
            try:
                # Texto recibido a un diccionario de Python
                paquete = json.loads(mensaje_texto) # Convierte JSON a diccionario
                
                if paquete.get("action") == "telemetry":   # Action: esta en sensor, indica mensaje. Para diferenciar tipos de msj
                    # Manda los datos del caballo en la cola para los Workers.
                    # El Gateway se desentiende y vuelve a escuchar.
                    cola_tareas.put(paquete)
                else:
                    print(f"[Gateway] Acción desconocida: {paquete.get('action')}")

            except json.JSONDecodeError:
                print(f"[Gateway] Error: Formato JSON inválido desde {direccion}")

    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"[Gateway] Error inesperado con {direccion}: {e}")
    finally:
        print(f"[Gateway] Cerrando conexión con {direccion}")
        writer.close()
        await writer.wait_closed()


async def iniciar_gateway(host, port, cola_tareas):
    """
    Levanta el servidor asincrónico y lo deja escuchando.
    """
    callback = functools.partial(manejar_cliente, cola_tareas=cola_tareas)
    
    servidor = await asyncio.start_server(callback, host, port)
    
    direcciones = ', '.join(str(sock.getsockname()) for sock in servidor.sockets)
    print(f"[Gateway] 🟢 Servidor AsyncIO escuchando telemetría en {direcciones}...")

    async with servidor:
        await servidor.serve_forever()