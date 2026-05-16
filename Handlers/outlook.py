import win32com.client 
import os


def prueba_conexion_outlook(log):
    
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        log.info("Conexión a outlook exitosa",extra={"origen":"script","destino":"script"})
        return outlook
    except Exception as e:
        log.error(f"Conexión a outlook fallida. {e}",extra={"origen":"script","destino":"script"})
        return False
    
