import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'maison_cafe'
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    print("✅ CONEXÃO OK!")
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("Tabelas:", tables)
    cursor.close()
    conn.close()
except Error as e:
    print("❌ ERRO:", e)
