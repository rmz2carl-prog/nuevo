from mysql_env import get_conn

def create_connection():
    return get_conn()

def close_connection(conn):
    if conn:
        conn.close()