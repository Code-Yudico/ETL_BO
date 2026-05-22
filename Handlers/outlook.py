from datetime import datetime,timedelta
import os
import win32com.client 
from Handlers.transformacion_archivos import  extrae_zip
import zipfile

def prueba_conexion_outlook(log): 
    
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        log.info("Conexión a outlook exitosa",extra={"origen":"script","destino":"script"})
        return outlook
    except Exception as e:
        log.error(f"Conexión a outlook fallida. {e}",extra={"origen":"script","destino":"script"})
        return False



def buscar_correos(outlook,asuntos,log_hist,log):
    
    try:
        namespace = outlook.GetNamespace("MAPI")
        bandeja_entrada = namespace.GetDefaultFolder(6)  # 6 corresponde a la bandeja de entrada
        correos = bandeja_entrada.Items
        log.info(f"{correos.Count} correos encontrados en bandeja de entrada",extra={"origen":"Outlook","destino":"script"})
        
        ultima_carga = log_hist.groupby("asunto")["fecha_recepcion"].max().to_dict()


        lista_descarga = []
        
        for asunto in asuntos:
            if asunto in ultima_carga:
                fecha=ultima_carga[asunto]
                
            else:
                fecha = datetime.today() - timedelta(days=30)
            
            fecha_str = fecha.strftime("%m/%d/%Y %I:%M %p")
            filtro = f"@SQL=\"urn:schemas:httpmail:subject\" = '{asunto}' AND \"urn:schemas:httpmail:datereceived\" > '{fecha_str}'"
            correos_filtrados = bandeja_entrada.Items.Restrict(filtro)
            correos_filtrados.Sort("[ReceivedTime]", False)  # False = ascendente
            for correo in correos_filtrados:
                lista_descarga.append(correo)
        

        return lista_descarga
    
    except Exception as e:
        log.error(f"No fue posible acceder a los correos. {e}",extra={"origen":"Outlook","destino":"script"})
        return False
    

def descargar_correos(lista_correos, directorio_temp, log):
    data_descarga=[]

    try:
        for correo in lista_correos:
            data_correos={"asunto":correo.Subject,"fecha_recepcion":correo.ReceivedTime,"archivos":[]}
            time_stamp=correo.ReceivedTime
            time_stamp_format= time_stamp.strftime("%Y%m%d_%H%M%S")

            for archivo in correo.Attachments:
                try:
                    nombre_archivo= archivo.FileName      
                    nuevo_nombre=f"{time_stamp_format}__{nombre_archivo}"
                    ruta_de_salvado=os.path.join(directorio_temp,nuevo_nombre)
                    archivo.SaveAsFile(ruta_de_salvado)
                    data_correos["archivos"].append(nuevo_nombre)
                    log.info(f"Archivo {nombre_archivo} del correo {correo.Subject} guardado y renombrado {nuevo_nombre}", extra={"origen":"outlook","destino":directorio_temp})
                    
                except Exception as e:
                    log.warning(f"Archivo {nombre_archivo} no guardado. Correo {correo.Subject} recibido el {time_stamp}. Pasando a siguiente correo/archivo. {e}", extra={"origen":"outlook","destino":directorio_temp})
                    continue               
            
            if not data_correos["archivos"]:
                log.warning(f"Correo {correo.Subject} sin archivos. Se omitirá de la lista de correos para procesamiento",extra={"origen":"outlook","destino":directorio_temp})
                continue
            
            data_descarga.append(data_correos)
        
        return data_descarga

    except Exception as e:
        log.error(f"No fue posible descargar los archivos adjuntos. {e}", extra={"origen":"outlook","destino":directorio_temp})
        return False
    


def obtener_adjuntos(obj_outlook,asuntos,log_hist,dir_temp,log):
    correos_a_descargar=buscar_correos(obj_outlook,asuntos,log_hist,log)
    if correos_a_descargar is False:
        log.error("No fue posible recuperar correos para descarga de outlook", extra={"origen":"outlook","destino":"script"})
        return False
    correos_descargados=descargar_correos(correos_a_descargar,dir_temp,log)
    if correos_descargados is False:
        log.error("No fue posible descargar adjuntos desde lista de correos outlook", extra={"origen":"outlook","destino":"script"})
        return False
    correos_finales=[]
    for correo in correos_descargados:
        nuevos_archivos=[]
        for adjunto in correo["archivos"]:
            if adjunto.endswith(".zip"):
                archivos_extraidos = extrae_zip(dir_temp,adjunto,log)
                if archivos_extraidos:
                    nuevos_archivos.extend(archivos_extraidos)
                    os.remove(os.path.join(dir_temp,adjunto))
                else:
                     log.warning(f"Zip {adjunto} del asunto {correo['asunto']} recibido el {correo['fecha_recepcion']} no pudo extraerse y ha sido omitido", extra={"origen":adjunto,"destino":"omitido"})
            else:
                nuevos_archivos.append(adjunto)
        if nuevos_archivos:
            correo["archivos"] = nuevos_archivos
            correos_finales.append(correo)
        else:
            log.warning(f"Correo {correo['asunto']} no tuvo archivos válidos después de procesar adjuntos y se omitirá para siguientes pasos", extra={"origen":correo["asunto"],"destino":"omitido"})
    return correos_finales