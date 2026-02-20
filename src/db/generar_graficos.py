import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import argparse

def graficar_signos_vitales(id_caballo, ruta_db="src/db/horsewatch.db"):
    # 1. Conectarnos a la base de datos
    try:
        conexion = sqlite3.connect(ruta_db)
        cursor = conexion.cursor()

        # 2. Extraer los datos ordenados por tiempo
        cursor.execute('''
            SELECT timestamp, bpm, temperatura 
            FROM telemetria 
            WHERE id_caballo = ? 
            ORDER BY timestamp ASC
        ''', (id_caballo,))
        
        datos = cursor.fetchall()
        conexion.close()
    except sqlite3.Error as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        return

    if not datos:
        print(f"⚠️ No se encontraron datos en la BD para el caballo: '{id_caballo}'")
        return

    # 3. Separar los datos en listas para el gráfico
    # Convertimos el texto del timestamp a un objeto datetime de Python
    tiempos = [datetime.fromisoformat(fila[0]) for fila in datos]
    bpms = [fila[1] for fila in datos]
    temperaturas = [fila[2] for fila in datos]

    # 4. Dibujar los gráficos
    plt.figure(figsize=(10, 6))

    # Primer gráfico: Ritmo Cardíaco (Arriba)
    plt.subplot(2, 1, 1)
    plt.plot(tiempos, bpms, marker='o', linestyle='-', color='red', label='BPM')
    plt.title(f'Evolución Clínica Histórica - Caballo: {id_caballo}')
    plt.ylabel('Ritmo Cardíaco (BPM)')
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Segundo gráfico: Temperatura (Abajo)
    plt.subplot(2, 1, 2)
    plt.plot(tiempos, temperaturas, marker='x', linestyle='--', color='orange', label='Temperatura (°C)')
    plt.xlabel('Hora de medición')
    plt.ylabel('Temperatura (°C)')
    plt.grid(True, alpha=0.3)
    plt.legend()

# Ajustar espacios y guardar como imagen
    plt.tight_layout()
    nombre_archivo = f"grafico_{id_caballo}.png"
    plt.savefig(nombre_archivo)
    print(f"📊 ¡Gráfico generado con éxito! Se guardó como '{nombre_archivo}' en la carpeta: ")
    # plt.show()  <-- No intenta abrir la ventana

if __name__ == '__main__':
    # Parseo de argumentos por CLI para hacerlo "On-Demand"
    parser = argparse.ArgumentParser(description="Generador de gráficos históricos - HorseWatch")
    parser.add_argument("--id", type=str, required=True, help="ID del caballo a graficar (ej: Tiro_Blanco)")
    
    args = parser.parse_args()
    
    graficar_signos_vitales(args.id)