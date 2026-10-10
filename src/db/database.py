from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from exceptions.base.system_error import DatabaseUnavailableError
import logging
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("MYSQL_NAME")
DB_USER = os.getenv("MYSQL_USER")
DB_PASS = os.getenv("MYSQL_PASS")
DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = os.getenv("MYSQL_PORT")

BASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}"
FULL_URL = f"{BASE_URL}/{DB_NAME}"
engine = create_engine(FULL_URL, pool_pre_ping=True) # pool_pre_ping=True - SQLAlchemy проверяет живое ли соединение 
                                                     #перед каждым запросом, предотвращая ошибку "MySQL server has gone away" в Docker
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db():
    temp_engine = create_engine(BASE_URL)
    try:
        with temp_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
            conn.commit()
        logging.info(f"База данных '{DB_NAME}' успешна инициализированна")
    except Exception as err:
        logging.critical(f"Не удалось инициализировать БД: {err}")
        raise DatabaseUnavailableError(str(err))
    finally:
        temp_engine.dispose()