import asyncio
import json
import functools

async def manejar_cliente(reader, writer, cola_tareas):
    """
    Corrutina que maneja la conexión individual de cada sensor.
    Es asincrónica, por lo que puede atender a miles de caballos a la vez.
    """
    direccion = writer.get_extra_info('peername')
    print(f"[Gateway] Nueva conexión desde el sensor en {direccion}")

    try:
        while True:
            # await: Permite que Python atienda a otros caballos mientras este envía datos
            data = await reader.readline()
            
            if not data:
                break # El sensor cerró la conexión

            mensaje_texto = data.decode().strip()
            
            try:
                # Convertimos el texto recibido a un diccionario de Python
                paquete = json.loads(mensaje_texto)
                
                if paquete.get("action") == "telemetry":
                    # Metemos los datos del caballo en la cola para los Workers.
                    # El Gateway se desentiende rápido y vuelve a escuchar.
                    cola_tareas.put(paquete)
                    # Opcional: imprimir para ver que está recibiendo
                    # print(f"[Gateway] Telemetría recibida de {paquete.get('id_caballo')}")
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
    # Usamos functools.partial para inyectar nuestra cola de tareas 
    # en la función manejar_cliente que requiere asyncio.start_server
    callback = functools.partial(manejar_cliente, cola_tareas=cola_tareas)
    
    servidor = await asyncio.start_server(callback, host, port)
    
    direcciones = ', '.join(str(sock.getsockname()) for sock in servidor.sockets)
    print(f"[Gateway] 🟢 Servidor AsyncIO escuchando telemetría en {direcciones}...")

    async with servidor:
        await servidor.serve_forever()