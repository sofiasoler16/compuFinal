import sqlite3
import time
import os

# Asegurate de que esta ruta apunte bien a tu base de datos
RUTA_DB = "src/db/horsewatch.db" 

def servidor_de_logs():
    print("🏥 --- SERVIDOR DE LOGS: HORSEWATCH --- 🏥")
    print("Esperando nuevas alertas críticas... (Presioná Ctrl+C para salir)\n")
    
    ultimo_timestamp = ""
    
    while True:
        try:
            conexion = sqlite3.connect(RUTA_DB)
            cursor = conexion.cursor()
            
            # Buscamos solo las alertas que sean MÁS NUEVAS que la última que imprimimos
            cursor.execute('''
                SELECT timestamp, id_caballo, alertas_generadas 
                FROM telemetria 
                WHERE alertas_generadas != '' AND alertas_generadas IS NOT NULL 
                AND timestamp > ?
                ORDER BY timestamp ASC
            ''', (ultimo_timestamp,))
            
            nuevas_alertas = cursor.fetchall()
            conexion.close()
            
            for alerta in nuevas_alertas:
                timestamp, caballo, detalle = alerta
                # Achicamos la fecha para que se vea solo la hora en la consola
                hora = timestamp.split("T")[1][:8] if "T" in timestamp else timestamp
                print(f"[LOG {hora}] 🚨 {caballo} -> {detalle}")
                
                # Actualizamos la memoria para no volver a imprimir esta alerta
                ultimo_timestamp = timestamp 
                
        except Exception as e:
            print(f"Error consultando la base de datos: {e}")
            
        # Esperamos 2 segundos antes de volver a preguntar para no saturar el disco
        time.sleep(2)

if __name__ == '__main__':
    servidor_de_logs()