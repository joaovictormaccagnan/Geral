import mysql.connector
from mysql.connector import Error

def criar_banco():
    conn = None
    try:
        conn = mysql.connector.connect(host='localhost', user='root', password='')
        cursor = conn.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS maison_cafe")
        cursor.execute("USE maison_cafe")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(100),
            itens JSON NOT NULL,
            pagamento VARCHAR(20) NOT NULL,
            total DECIMAL(10,2) NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        print("✅ Banco e tabela 'pedidos' criados!")
        
    except Error as e:
        print(f"❌ Erro: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    criar_banco()
