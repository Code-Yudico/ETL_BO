import os
from dotenv import load_dotenv
import time
import glob
import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import win32com.client
import urllib
import warnings
import logging



#   Configurar las credenciales del .env
load_dotenv()
DB_SERVER=os.getenv("DB_SERVER")
DB_DATABASE=os.getenv("DB_DATABASE")
DB_USER=os.getenv("DB_USER")
DB_PASS=os.getenv("DB_PASS")
DB_DRIVER=os.getenv("DB_DRIVER")

#   Directorio de trabajo
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
#   Directorio del archivo txt de logging
log_path = os.path.join(BASE_DIR, 'logger_BO.txt') 


#Inicializar el engine object
connection_str = f'DRIVER={{{DB_DRIVER}}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USER};PWD={DB_PASS};'
connection_str_parsed = f"mssql+pyodbc://?odbc_connect={urllib.parse.quote_plus(connection_str)}"
engine= create_engine(connection_str_parsed)

######################################################################################################################################################
#   Configuración del módulo logging


logger=logging.getLogger("ETL_BO")
logger.setLevel(logging.DEBUG)
# NIVELES:  DEBUG → INFO → WARNING → ERROR → CRITICAL

#   Usa método de format string antiguo de Python para retrocompatibilidad con otros sistemas
formatter=logging.Formatter("%(asctime)s | %(levelname)s | %(origen)s -> %(destino)s | %(message)s")

#   Configuración del handler para escribir en txt
txt_handler=logging.FileHandler(log_path,encoding="UTF-8")
txt_handler.setFormatter(formatter)
logger.addHandler(txt_handler)

#   Configuración para imprimir los logs en consola durante ejecuciones manuales
console_handler=logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

#   EJEMPLO DE LLAMAR A logger
#   logger.info("Conexión exitosa",extra={"origen":"script","destino":"SQL"})

######################################################################################################################################################
class Logger:
    def __init__(self, ruta_archivo,sql_engine=None):
        #abre el archivo txt en modo append "a" 
        self.archivo= open(ruta_archivo,'a',encoding='utf-8')
        self.engine = sql_engine

        if sql_engine is None:
            warnings.warn("No se proporcionó un engine. Los logs no se escribiran en SQL")

        if sql_engine is not None and not isinstance(self.engine, sqlalchemy.engine.Engine):
            raise TypeError("Se espera un objeto engine de SQLAlchemy")
        
        
        self.lista_logs = []
    
    def escribir(self, mensaje, nivel="INFO",origen="N/A",destino="N/A"):
        #Inserta un timestamp para cada registro del log.
        
        registro = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nivel": nivel,
            "origen":origen,
            "destino": destino,
            "mensaje":mensaje
        }
        
        linea_txt=f"{registro['timestamp']} | {nivel} | {origen} -> {destino} | {mensaje}\n"
        self.archivo.write(linea_txt)
        self.lista_logs.append(registro)

#>>NOTA: Porción comentada durante pruebas hasta que se comienze a cargar los logs a SQL

#         if len(self.lista_logs) >=50:
#             self.enviar_a_sql()


#     def enviar_a_sql(self):
#         if self.lista_logs:
#             print(f"Subiendo {len(self.lista_logs)} registros a la base de datos.")

#             #Lógica de carga a SQL
#             df_logs = pd.DataFrame(self.lista_logs)

# #>>NOTA: ¿Cómo se puede refactorizar para tener acceso fácil a la variable de tabla de carga de logs?
           
#             df_logs.to_sql('tbl_logs_ETL_BO',con=self.engine,if_exists='append',index=False)
#             self.lista_logs = []   
    
    def close(self):
#        Descomentar cuando se active la escritura de logs a SQL
#        self.enviar_a_sql()
        self.archivo.close()

#Inicializar logger object
n_log = Logger(log_path)

######################################################################################################################################################


def  prueba_conexion_sql(engine,log,t_espera=3):
    
    intentos = 0 

    while intentos < 3:
        try:
            with engine.connect() as connection:
                log.info("Conexión exitosa a SQL",extra={"origen":"script","destino":"SQL"})
                return True
        except sqlalchemy.exc.SQLAlchemyError as e:
            intentos += 1
            log.error(f"Intento {intentos}. Reintento en {t_espera} segundos. {e}",extra={"origen":"script","destino":"SQL"})        
            time.sleep(t_espera)
    
    return False


if not prueba_conexion_sql(engine,logger):
    logger.critical(f"No fue posible conectarse a SQL. Script cancelado",extra={"origen":"script","destino":"SQL"})
    txt_handler.close()
    exit(1)    

"""
1 correos_a_descargar = buscar_coreos(outlook, asuntos, log_hist, log)

2 si correos_a_descargar is false terminar ejecución

3 correos_descargados = descargar_correos(correos_a_descargar,dir_temp,log)

4 log de data_descarga

5 si correos_descargados is false terminar ejecución



6 


correos_finales=[]
para cada elemento_de_la_lista en correos_descargados:
	nuevos_archivos=[]
	para cada adjunto en elemento_de_la_lista["archivos"]
		si adjunto termina en .zip:
			archivos_extraidos = extrae_zip()
			si archivos_extraidos:
				nuevos_archivos.extend(archivos_extraidos)
                os.remove(os.path.join(dir_temp,adjunto))
			else:
                log.warning(f"Zip {adjunto} del asunto {elemento_de_la_lista["asunto"]} no pudo extraerse y ha sido omitido")
		else:
			nuevos_archivos.append(adjunto)
	if nuevos_archivos:
        elemento_de_la_lista["archivos"] = nuevos_archivos
        correos_finales.append(elemento_de_la_lista)
	else:	
        log.warning(f"Correo {elemento_de_la_lista["asunto"]} quedó sin archivos válidos después de procesar adjuntos")
return correos finales
"""