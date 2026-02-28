"""Conexión a la base de datos con context manager."""
import psycopg2
from contextlib import contextmanager
from config import PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD

@contextmanager
def get_conn():
    """Abre conexión y garantiza cierre (incluso con excepciones)."""
    conn = psycopg2.connect(
        host=PGHOST,
        port=PGPORT,
        dbname=PGDATABASE,
        user=PGUSER,
        password=PGPASSWORD,
    )
    try:
        yield conn
    finally:
        conn.close()
