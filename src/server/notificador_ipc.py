import smtplib
import time
import queue # Necesario para manejar el timeout de la cola
from email.mime.text import MIMEText

# Configuración del servidor SMTP
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
FROM_ADDRESS = "sofiasoler16044@gmail.com" 
SMTP_USER = "sofiasoler16044@gmail.com"  
SMTP_PASSWORD = "zydo ihey jroe nbxa"        
VETERINARIO_EMAIL = "veterinario@ejemplo.com" 

# Configuración de la Ventana de Tiempo
VENTANA_SEGUNDOS = 60 # 300 son 5 minutos
ALERTAS_MINIMAS = 2   # Cuántas alertas en esa ventana justifican un mail

def enviar_email(asunto, cuerpo):
    """Función para mandar el email vía Gmail."""
    msg = MIMEText(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = FROM_ADDRESS
    msg['To'] = VETERINARIO_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()  
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"[Notificador] 📧 ¡EMAIL ENVIADO! ({VETERINARIO_EMAIL})")
    except Exception as e:
        print(f"[Notificador] ❌ Error al enviar email: {e}")

def iniciar_notificador(cola_ipc):
    print("[Notificador] Proceso independiente iniciado. Escuchando canal IPC...")
    
    # Diccionario para agrupar alertas. 
    # Formato: {"Tiro_Blanco": {"conteo": 0, "inicio_ventana": time.time(), "ultima_alerta": ""}}
    agrupador = {}

    while True:
        tiempo_actual = time.time()

        # 1. INTENTAR RECIBIR MENSAJES (con timeout para no quedarnos congelados)
        try:
            datos_alerta = cola_ipc.get(timeout=1.0)
            caballo = datos_alerta["caballo"]
            mensaje_alerta = datos_alerta["mensaje"]
            
            # ---> ALERTA POR TERMINAL (Siempre ocurre de forma inmediata) <---
            # print(f"🖥️ [TERMINAL] Alerta en tiempo real -> {mensaje_alerta}")

            # ---> REGISTRAR PARA EL CORREO (Agrupación) <---
            if caballo not in agrupador:
                agrupador[caballo] = {
                    "conteo": 1, 
                    "inicio_ventana": tiempo_actual, 
                    "ultima_alerta": mensaje_alerta
                }
            else:
                agrupador[caballo]["conteo"] += 1
                agrupador[caballo]["ultima_alerta"] = mensaje_alerta

        except queue.Empty:
            # No llegó ningún mensaje en este segundo, no pasa nada.
            # Pasamos directo a revisar el reloj.
            pass

        # 2. REVISAR SI SE CUMPLIÓ EL TIEMPO PARA ENVIAR CORREOS
        tiempo_actual = time.time() # Actualizamos la hora
        
        # Iteramos sobre una lista de las llaves para poder borrar elementos sin error
        for caballo in list(agrupador.keys()):
            datos = agrupador[caballo]
            tiempo_transcurrido = tiempo_actual - datos["inicio_ventana"]
            
            # Si ya pasó la ventana de tiempo (ej: 5 minutos)...
            if tiempo_transcurrido >= VENTANA_SEGUNDOS:
                
                # Revisamos si superó el umbral de alertas mínimas
                if datos["conteo"] >= ALERTAS_MINIMAS:
                    print("\n" + "="*60)
                    print(f"🚨 [PROCESO NOTIFICADOR] Criterio crítico cumplido para {caballo} 🚨")
                    print(f"Generó {datos['conteo']} alertas en los últimos {VENTANA_SEGUNDOS} segundos.")
                    print("="*60 + "\n")
                    
                    asunto = f"🚨 URGENTE: Múltiples alertas para {caballo}"
                    cuerpo = (
                        f"Sistema de Monitoreo Equino Automático:\n\n"
                        f"El caballo '{caballo}' ha generado {datos['conteo']} alertas críticas "
                        f"en un lapso de {VENTANA_SEGUNDOS} segundos.\n\n"
                        f"Última alerta registrada:\n{datos['ultima_alerta']}\n\n"
                        f"Por favor, que el veterinario de guardia revise el box de inmediato."
                    )
                    enviar_email(asunto, cuerpo)
                else:
                    # Hubo alertas, pero fueron muy pocas (falsa alarma o algo aislado)
                    print(f"ℹ️ [Notificador] Se ignoran alertas previas de {caballo} (Solo tuvo {datos['conteo']}, no superó el mínimo de {ALERTAS_MINIMAS}).")

                # Limpiamos el registro de este caballo para iniciar una nueva ventana en el futuro
                del agrupador[caballo]