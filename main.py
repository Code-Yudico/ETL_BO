import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine, text
import warnings
import logging
import urllib
import sys
from Handlers.sql import prueba_conexion_sql


#   Configurar las credenciales del .env



################################################################################################
#   Definición de funciones orquestadoras

def inicializar_logger(base_dir):
    #   Directorio del archivo txt de logging
    log_path = os.path.join(base_dir, 'logger_BO.txt')
    
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
    return logger

    #   EJEMPLO DE LLAMAR A logger
    #   logger.info("Conexión exitosa",extra={"origen":"script","destino":"SQL"})


def inicializar_engine():
    DB_SERVER=os.getenv("DB_SERVER")
    DB_DATABASE=os.getenv("DB_DATABASE")
    DB_USER=os.getenv("DB_USER")
    DB_PASS=os.getenv("DB_PASS")
    DB_DRIVER=os.getenv("DB_DRIVER")
    #Inicializar el engine object
    connection_str = f'DRIVER={{{DB_DRIVER}}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USER};PWD={DB_PASS};'
    connection_str_parsed = f"mssql+pyodbc://?odbc_connect={urllib.parse.quote_plus(connection_str)}"
    engine= create_engine(connection_str_parsed)
    return engine

def prueba_condiciones_de_ejecucion():
    pass

def descarga_outlook():
    pass

def procesa_archvios():
    pass

def carga_sql():
    pass

def descarga_vistas_sql():
    pass

def envio_correos():
    pass

################################################################################################
#   dfinición del main

def main():
    load_dotenv()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
    logger= inicializar_logger(BASE_DIR)
    engine=inicializar_engine()
    

    if not prueba_condiciones_de_ejecucion(logger, engine):
        exit(1)
    

    descarga_outlook(logger)

    procesa_archvios(logger)

    carga_sql(engine,logger)

    descarga_vistas_sql(engine,logger)

    envio_correos(logger)


################################################################################################
#   main

if __name__ == "__main__":
    main()


