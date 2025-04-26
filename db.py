import mysql.connector
from mysql.connector import errorcode
from pathlib import Path

# Configurazione MySQL: aggiornare host, port, user, password, database
DB_CONFIG = {
    'host': '127.0.0.1',         # o IP del server
    'port': 3306,
    'user': 'root',
    'password': 'pwd',
    'database': 'padel_db',
    'autocommit': False,
    'raise_on_warnings': True
}

SCHEMA_FILE = Path(__file__).parent / 'schema.sql'

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        # Messaggio di debug
        raise RuntimeError(
            f"Impossibile connettersi a MySQL {DB_CONFIG['host']}:{DB_CONFIG['port']}: {err.msg}"
        )

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    sql = SCHEMA_FILE.read_text()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    print("Database inizializzato.")

if __name__ == '__main__':
    init_db()