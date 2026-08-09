import os
import psycopg2

from dotenv import load_dotenv

load_dotenv()

def connect_db():
    print(os.getenv("DB_HOST"))
    try:
        conn = psycopg2.connect(
            database = os.getenv("DB_NAME"),
            user = os.getenv("DB_USER"),
            host = os.getenv("DB_HOST"),
            password = os.getenv("DB_PASSWORD"),
            port = os.getenv("DB_PORT"),
        )
        print("Conexão com banco de dados sucedida com sucesso.")

    except Exception as e:
        print(f"Erro ao conectar com o banco: {e}")
        return None

    return conn


connect_db()