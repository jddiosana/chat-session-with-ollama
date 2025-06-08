import psycopg

from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "chat-history")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")

conn_info = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"
sync_connection = psycopg.connect(conn_info)

def get_connection():
    return psycopg.connect(conn_info)