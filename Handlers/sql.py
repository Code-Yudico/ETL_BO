import time
import sqlalchemy
import logging
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