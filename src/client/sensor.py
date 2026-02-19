import socket
import json
import time
import random
import argparse
from datetime import datetime

def simular_datos(id_caballo, modo):
    """Genera datos biométricos simulados según el estado del caballo."""
    if modo == "colico":
        # Simulamos parámetros anormales (dolor/estrés)
        bpm = random.randint(60, 85)  # Taquicardia
        temp = round(random.uniform(38.5, 39.5), 1)  # Fiebre leve a moderada
        actividad = random.choice(["inmovil", "revolcandose"])
    else:
        # Simulamos un caballo sano en su box
        bpm = random.randint(30, 45)  # Reposo normal
        temp = round(random.uniform(37.5, 38.2), 1)  # Temperatura normal
        actividad = random.choice(["comiendo", "descansando", "caminando_lento"])

    return {
        "action": "telemetry",
        "id_caballo": id_caballo,
        "timestamp": datetime.now().isoformat(),
        "bpm": bpm,
        "temperatura": temp,
        "actividad": actividad
    }

def iniciar_sensor(host, port, id_caballo, modo, intervalo):
    # Usamos IPv4 por defecto, creando el socket TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            print(f"[{id_caballo}] Intentando conectar al Gateway en {host}:{port}...")
            s.connect((host, port))
            print(f"[{id_caballo}] ¡Conectado exitosamente!")

            while True:
                # 1. Generar la telemetría
                datos = simular_datos(id_caballo, modo)
                
                # 2. Convertir el diccionario a JSON y luego a bytes
                mensaje = json.dumps(datos) + "\n"
                
                # 3. Enviar por el socket
                s.sendall(mensaje.encode('utf-8'))
                print(f"[{id_caballo}] Datos enviados: {datos['bpm']} lpm, {datos['temperatura']}°C, {datos['actividad']}")
                
                # 4. Esperar hasta el próximo envío
                time.sleep(intervalo)

        except ConnectionRefusedError:
            print(f"[{id_caballo}] Error: El servidor no está corriendo o rechazó la conexión.")
        except KeyboardInterrupt:
            print(f"\n[{id_caballo}] Sensor apagado manualmente.")
        except Exception as e:
            print(f"[{id_caballo}] Error inesperado: {e}")

if __name__ == "__main__":
    # Parseo de argumentos por línea de comandos (Requisito de la cátedra)
    parser = argparse.ArgumentParser(description="Simulador de Sensor Equino - HorseWatch")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="IP del servidor Gateway")
    parser.add_argument("--port", type=int, default=8888, help="Puerto del servidor Gateway")
    parser.add_argument("--id", type=str, required=True, help="Identificador del caballo (ej. box_01)")
    parser.add_argument("--modo", type=str, choices=["sano", "colico"], default="sano", help="Estado de salud a simular")
    parser.add_argument("--intervalo", type=float, default=2.0, help="Segundos entre cada envío de datos")

    args = parser.parse_args()

    iniciar_sensor(args.host, args.port, args.id, args.modo, args.intervalo)