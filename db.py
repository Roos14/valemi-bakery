# db.py
import os
import mysql.connector
from urllib.parse import urlparse

def get_connection():
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        # 👉 Modo producción (Render + Railway)
        url = urlparse(db_url)
        return mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            database=url.path[1:],
            port=url.port
        )
    else:
        # 👉 Modo local
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="valemi_bakery"
        )
