from flask import Flask, send_file
import sqlite3
import matplotlib
matplotlib.use('Agg') # Fundamental para servidores web
import matplotlib.pyplot as plt
import io

app = Flask(__name__)
RUTA_DB = "src/db/horsewatch.db"

@app.route('/')
def inicio():
    """Página de inicio súper simple."""
    return '''
    <h1>🐴 Panel Clínico - HorseWatch</h1>
    <p>Para ver el gráfico en vivo, hacé clic en el caballo:</p>
    <ul>
        <li><a href="/grafico/Tiro_Blanco">Ver gráfico de Tiro_Blanco</a></li>
        <li><a href="/grafico/Spirit">Ver gráfico de Spirit</a></li>
    </ul>
    '''

@app.route('/grafico/<id_caballo>')
def generar_grafico(id_caballo):
    """Consulta la BD, dibuja el gráfico y lo manda como imagen a la web."""
    try:
        conexion = sqlite3.connect(RUTA_DB)
        cursor = conexion.cursor()
        # Traemos solo las últimas 50 mediciones para que el gráfico no sea un masacote
        cursor.execute('''
            SELECT timestamp, bpm, temperatura 
            FROM telemetria 
            WHERE id_caballo = ? 
            ORDER BY timestamp DESC LIMIT 50
        ''', (id_caballo,))
        datos = cursor.fetchall()
        conexion.close()
    except Exception as e:
        return f"Error de base de datos: {e}", 500

    if not datos:
        return f"<h2>Aún no hay datos para el caballo: {id_caballo}</h2>", 404

    # Damos vuelta los datos para que el tiempo avance de izquierda a derecha
    datos.reverse()
    
    # Preparamos las listas
    tiempos = [d[0].split("T")[1][:8] if "T" in d[0] else d[0][-8:] for d in datos]
    bpms = [d[1] for d in datos]
    temps = [d[2] for d in datos]

    # Armamos el gráfico doble
    plt.figure(figsize=(10, 6))
    
    plt.subplot(2, 1, 1)
    plt.plot(tiempos, bpms, color='red', marker='o', label='BPM')
    plt.title(f"Evolución Clínica - {id_caballo}")
    plt.ylabel("BPM")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xticks([]) # Ocultamos la hora arriba para que no se superponga
    
    plt.subplot(2, 1, 2)
    plt.plot(tiempos, temps, color='orange', marker='x', label='Temperatura (°C)')
    plt.ylabel("Temp (°C)")
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.tight_layout()

    # Guardamos el gráfico en la RAM (buffer) y se lo mandamos al navegador
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close() # Limpiamos la memoria para que no explote el servidor

    return send_file(img_buffer, mimetype='image/png')

if __name__ == '__main__':
    print("🌐 Servidor Web iniciado. Entrá a http://127.0.0.1:5000 en tu navegador.")
    # El host 0.0.0.0 lo deja listo para cuando le metamos Docker
    app.run(host='0.0.0.0', port=5000)