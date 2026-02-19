import sqlite3
import os

def inicializar_bd():
    # Asegurarnos de que estamos en la carpeta correcta
    os.makedirs("src/db", exist_ok=True)
    ruta_db = "src/db/horsewatch.db"
    
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()

    # Creamos la tabla principal de telemetría
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            id_caballo TEXT NOT NULL,
            bpm INTEGER,
            temperatura REAL,
            actividad TEXT,
            alertas_generadas TEXT
        )
    ''')

    conexion.commit()
    conexion.close()
    print("✅ Base de datos 'horsewatch.db' y tabla 'telemetria' creadas con éxito.")

if __name__ == "__main__":
    inicializar_bd()