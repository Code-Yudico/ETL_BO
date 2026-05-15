import os
import time
import datetime
import pandas as pd



def archivo_a_dataframe(ruta_archivo, config,log):
    
    nombre,ext = os.path.splitext(ruta_archivo)

    try:
        if ext.lower() in (".xlsx", ".xls"):
            df = pd.read_excel(ruta_archivo)
            log.info(f"Archivo {nombre}{ext} leído exitosamente.", extra={"origen":f"{nombre}{ext}","destino":"dataframe"})            
        elif ext.lower() == ".csv":
            df =pd.read_csv(ruta_archivo,encoding=config["encoding"])
            log.info(f"Archivo{nombre}{ext} leído exitosamente.",extra={"origen":f"{nombre}{ext}","destino":"dataframe"})      
        elif ext.lower() == ".txt":
            df =pd.read_csv(ruta_archivo,sep=config["separador"],encoding=config["encoding"])
            log.info(f"Archivo{nombre}{ext} leído exitosamente.",extra={"origen":f"{nombre}{ext}","destino":"dataframe"})       
        else:
            log.error(f"Archivo {nombre} con extensión {ext} no soportada.",extra={"origen":f"{nombre}{ext}","destino":"dataframe"})
            return False

    except Exception as e:
        log.error(f"No fue posible leer el archivo {nombre}{ext}. {e}", extra={"origen":f"{nombre}{ext}","destino":"dataframe"})
        return False
    
    try:
        df.rename(columns=str.lower, inplace=True)
        df.rename(columns=config["nombres_columnas"],inplace=True)
        df = df.astype(config["datatypes"])
        return df

    except Exception as e:
        log.error(f"No fue posible transofrmar el archivo{nombre}{ext}. {e}", extra={"origen":f"{nombre}{ext}","destino":"dataframe"})
        return False


def exportar_excel(df, ruta):
    pass