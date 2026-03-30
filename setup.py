import mysql.connector
from mysql.connector import Error
import bcrypt

def criar_banco():
    conn = None
    try:
        conn = mysql.connector.connect(host='localhost', user='root', password='12345678')
        cursor = conn.cursor()
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS maison_cafe")
        cursor.execute("USE maison_cafe")
        
        # Tabela usuarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario VARCHAR(50) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabela pedidos
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
        
        # ✅ USUÁRIO PADRÃO CORRETO (senha123 criptografada)
        senha_hash = bcrypt.hashpw("senha123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("""
            INSERT IGNORE INTO usuarios (usuario, senha) 
            VALUES ('admin', %s)
        """, (senha_hash,))
        
        conn.commit()
        print("✅ ✅ USUÁRIO CRIADO: admin / senha123")
        print("✅ Banco e tabelas OK!")
        
    except Error as e:
        print(f"❌ Erro: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    criar_banco()
