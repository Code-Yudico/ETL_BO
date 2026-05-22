import time
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError, ProgrammingError
import pandas as pd


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


def sql_push(engine, data, table,log):
    try:
        data.to_sql(table,con=engine,if_exists="append",index=False)
        log.info(f"Carga exitosa",extra={"origen":"script","destino":"SQL"})
        return True
    except (DatabaseError,ProgrammingError) as e:
        log.error(f"Carga fallida, error de SQL:{e}",extra={"origen":"script","destino":"SQL"})
        return False
    except Exception as e:
        log.error(f"Carga fallida, error general:{e}",extra={"origen":"script","destino":"SQL"})
        return False


def sql_pull(engine,view,log):
    query=f"SELECT * FROM {view}"
    try:
        df = pd.read_sql(query,con=engine)
        log.info(f"Descarga de {view} exitosa.",extra={"origen":"SQL","destino":"dataframe"})
        return df
    except (DatabaseError,ProgrammingError) as e:
        log.error(f"Descarga fallida de {view}: {e}",extra={"origen":"SQL","destino":"dataframe"})
        return False
    except Exception as e:
        log.error(f"Descarga fallida de {view}: {e}",extra={"origen":"SQL","destino":"dataframe"})
        return False

def log_cargas(engine, tabla_logs, log):
    try:
        query=f"WITH CARGAS AS (SELECT ROW_NUMBER() OVER (PARTITION BY asunto ORDER BY fecha_recepcion DESC) AS rank, * FROM {tabla_logs}) SELECT asunto, fecha_recepcion, fecha_carga FROM CARGAS WHERE RANK = 1"
        df=pd.read_sql(query,engine)
        log.info(f"Histórico de ejeciciónes cargado exitosamente desde {tabla_logs}", extra={"origen":"sql","destino":"dataframe"})
        return df
    except Exception as e:
        log.error(f"Error al cargar histórico de ejecuciones. {e}", extra={"origen":"sql","destino":"dataframe"})
        return False
    

def inicializar_tabla_control(engine, tabla, log):
    ddl = f"""
    IF OBJECT_ID('{tabla}', 'U') IS NULL
    BEGIN
        CREATE TABLE {tabla} (
            asunto NVARCHAR(255),
            fecha_recepcion DATETIME2,
            fecha_carga DATETIME2
        )
    END
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(ddl))
            conn.commit()
        log.info(f"Tabla {tabla} verificada/creada.", extra={"origen":"sql","destino":tabla})
        return True
    except Exception as e:
        log.error(f"Error al verificar/crear {tabla}. {e}", extra={"origen":"sql","destino":tabla})
        return False