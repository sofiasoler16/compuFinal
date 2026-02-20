import sqlite3
import time
import os
import sys

# Agregamos la ruta para poder importar tu generador de gráficos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db')))
from generar_graficos import graficar_signos_vitales

RUTA_DB = "src/db/horsewatch.db"

def mostrar_ultimas_alertas(limite=10):
    """Consulta la base de datos para mostrar las alertas más recientes."""
    try:
        conexion = sqlite3.connect(RUTA_DB)
        cursor = conexion.cursor()
        # Buscamos registros donde el texto de alertas no esté vacío
        cursor.execute('''
            SELECT timestamp, id_caballo, alertas_generadas 
            FROM telemetria 
            WHERE alertas_generadas != '' 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limite,))
        
        alertas = cursor.fetchall()
        conexion.close()

        print("\n" + "="*50)
        print(" 📋 ÚLTIMAS ALERTAS REGISTRADAS EN EL SISTEMA ")
        print("="*50)
        
        if not alertas:
            print("✅ No hay alertas recientes. Todos los caballos están estables.")
        else:
            for alerta in alertas:
                fecha, caballo, detalle = alerta
                # Formateamos la fecha para que sea más legible
                hora = fecha.split("T")[1][:8] 
                print(f"[{hora}] 🐴 {caballo} -> ⚠️ {detalle}")
        print("="*50 + "\n")

    except sqlite3.Error as e:
        print(f"❌ Error al consultar la base de datos: {e}")

def menu_principal():
    """Bucle interactivo para el veterinario."""
    while True:
        print("\n🏥 --- PANEL DE CONTROL VETERINARIO - HORSEWATCH --- 🏥")
        print("1. Ver historial de alertas recientes")
        print("2. Generar gráfico clínico de un caballo")
        print("3. Salir")
        
        opcion = input("\nSeleccione una opción (1-3): ")

        if opcion == '1':
            mostrar_ultimas_alertas()
            input("Presione ENTER para volver al menú...")
            
        elif opcion == '2':
            caballo_id = input("Ingrese el ID del caballo a graficar (ej: Tiro_Blanco): ")
            print(f"\n📊 Generando gráficos para {caballo_id}...")
            # Llamamos a la función que armamos en el paso anterior
            graficar_signos_vitales(caballo_id)
            
        elif opcion == '3':
            print("Cerrando Panel de Control. ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida. Intente de nuevo.")

if __name__ == '__main__':
    # Limpiamos la consola para que se vea prolijo
    os.system('cls' if os.name == 'nt' else 'clear')
    menu_principal()