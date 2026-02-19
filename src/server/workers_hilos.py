import time
import sqlite3

def iniciar_worker(id_worker, cola_tareas, cola_ipc, lock_db, historial, lock_memoria, ruta_db="src/db/horsewatch.db"):
    print(f"[Worker-{id_worker}] Hilo listo y conectado a la BD...")
    
    # Cada hilo tiene su propia conexión a SQLite (requerimiento de la librería sqlite3)
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()
    
    while True:
        paquete = cola_tareas.get()
        caballo = paquete.get("id_caballo")
        bpm = paquete.get("bpm", 0)
        temp = paquete.get("temperatura", 0.0)
        actividad = paquete.get("actividad", "")
        timestamp = paquete.get("timestamp")
        
        alertas_actuales = []
        
        # 1. REGLAS SIN ESTADO
        if bpm > 60:
            alertas_actuales.append(f"Taquicardia ({bpm} lpm)")
        if temp > 38.5:
            alertas_actuales.append(f"Fiebre ({temp}°C)")

        # 2. REGLA CON ESTADO (Revolcadas y Filtro de Alertas)
        with lock_memoria:
            if caballo not in historial:
                # Agregamos "ultimo_aviso" para saber cuándo le hablamos al Notificador por última vez
                historial[caballo] = {"revolcadas": 0, "inicio_ventana": time.time(), "ultimo_aviso": 0}
            
            tiempo_actual = time.time()
            if tiempo_actual - historial[caballo]["inicio_ventana"] > 60:
                historial[caballo]["revolcadas"] = 0
                historial[caballo]["inicio_ventana"] = tiempo_actual

            if actividad == "revolcandose":
                historial[caballo]["revolcadas"] += 1
                
            if historial[caballo]["revolcadas"] >= 5:
                alertas_actuales.append(f"Posible Cólico (Se revolcó {historial[caballo]['revolcadas']} veces)")
                historial[caballo]["revolcadas"] = 0 

            # 3. ENVIAR AL NOTIFICADOR POR IPC (CON LÍMITE DE 5 SEGUNDOS)
            texto_alertas = "" # <-- LA CREAMOS ACÁ SIEMPRE PARA QUE LA BD NO FALLE
            
            if len(alertas_actuales) > 0:
                texto_alertas = " | ".join(alertas_actuales) # La llenamos con texto
                
                # Solo mandamos el mensaje IPC si pasaron más de 5 segundos desde el último
                if tiempo_actual - historial[caballo]["ultimo_aviso"] >= 5.0:
                    mensaje_alerta = f"¡ALERTA {caballo}! Presenta: {texto_alertas}."
                    
                    cola_ipc.put({
                        "caballo": caballo,
                        "mensaje": mensaje_alerta
                    })
                    
                    # Actualizamos el reloj de este caballo
                    historial[caballo]["ultimo_aviso"] = tiempo_actual
            
        # 4. GUARDAR EN BASE DE DATOS (CONCURRENCIA SEGURA)
        # Usamos lock_db para que dos hilos no intenten escribir en el archivo .db al mismo milisegundo
        with lock_db:
            try:
                cursor.execute('''
                    INSERT INTO telemetria (timestamp, id_caballo, bpm, temperatura, actividad, alertas_generadas)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (timestamp, caballo, bpm, temp, actividad, texto_alertas))
                conexion.commit()
            except sqlite3.Error as e:
                print(f"[Worker-{id_worker}] Error guardando en BD: {e}")
        
        cola_tareas.task_done()