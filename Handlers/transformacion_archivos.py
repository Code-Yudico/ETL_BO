import os
import pandas as pd
import zipfile



def extrae_zip(ruta,nombre_archivo,log):
    archivo=f"{ruta}/{nombre_archivo}"
    try:
        with zipfile.ZipFile(archivo,"r") as zip:
            zip.extractall(ruta)    
        log.info("Archivo extraido exitosamente",extra={"origen":f"Archivo Zip:{nombre_archivo}","destino":f"Carpeta de descargas:{ruta}"})
        return True
    
    except Exception as e:
        log.error(f"Extracción de Zip fallida. {e}",extra={"origen":f"Archivo Zip:{nombre_archivo}","destino":f"Carpeta de descargas:{ruta}"})
        return False


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
        log.info(f"Columnas de {nombre}{ext} modificadas exitosamente. Columnas modificadas:{config["nombrecolumnas"]}",extra={"origen":f"{nombre}{ext}","destino":"dataframe"})
        df = df.astype(config["datatypes"])
        return df

    except Exception as e:
        log.error(f"No fue posible transofrmar el archivo{nombre}{ext}. {e}", extra={"origen":f"{nombre}{ext}","destino":"dataframe"})
        return False


def exportar_excel(df, ruta, nombre_archivo,log):
    
    try:
        archivo=f"{ruta}/{nombre_archivo}.xlsx"
        df.to_excel(archivo,index=False)
        log.info(f"Archivo {nombre_archivo} exportado a excel exitosamente.",extra={"origen":"dataframe view","destino":"excel file"})
        return True
    
    except Exception as e:
        log.error(f"El el dataframe no pudo ser exportado a Excel. {e}",extra={"origen":f"dataframe de {nombre_archivo}","destino":"excel"})
        return False