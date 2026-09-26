from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("MYSQL_NAME")
DB_USER = os.getenv("MYSQL_USER")
DB_PASS = os.getenv("MYSQL_PASS")
DB_HOST = os.getenv("MYSQL_HOST")
DB_PORT = os.getenv("MYSQL_PORT")

def create_database():
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}")
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
        conn.commit()

def get_engine():
    return create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

create_database()
engine = get_engine()
SessionLocal = sessionmaker(bind=engine)

def init_db():
    return SessionLocal()