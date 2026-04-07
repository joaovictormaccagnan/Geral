import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='maison_cafe'
    )
    cursor = conn.cursor()
    
    # Criar tabela de usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print("✅ Tabela 'usuarios' criada com sucesso!")
    
    # Criar tabela de pedidos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario VARCHAR(100),
        itens JSON NOT NULL,
        pagamento VARCHAR(20) NOT NULL,
        total DECIMAL(10,2) NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario) REFERENCES usuarios(usuario)
    )
    """)
    conn.commit()
    print("✅ Tabela 'pedidos' criada com sucesso!")
    
    # Criar tabela de logins (para registrar cada login)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logins (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario VARCHAR(100) NOT NULL,
        data_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario) REFERENCES usuarios(usuario)
    )
    """)
    conn.commit()
    print("✅ Tabela 'logins' criada com sucesso!")
    
    # Criar tabela de cardápio
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cardapio (
        id INT AUTO_INCREMENT PRIMARY KEY,
        categoria VARCHAR(50) NOT NULL,
        nome VARCHAR(100) NOT NULL,
        preco DECIMAL(10,2) NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    print("✅ Tabela 'cardápio' criada com sucesso!")
    
    # Inserir cardápio padrão se ainda não existir
    cursor.execute("SELECT COUNT(*) as count FROM cardapio")
    result = cursor.fetchone()
    count = result[0] if isinstance(result, tuple) else result['count']
    if count == 0:
        cardapio_padrao = [
            # Bebidas
            ('Bebidas', 'Café expresso', 5.00),
            ('Bebidas', 'Café com leite', 6.00),
            ('Bebidas', 'Cappuccino', 8.00),
            ('Bebidas', 'Chocolate quente', 7.00),
            ('Bebidas', 'Chá', 4.00),
            ('Bebidas', 'Suco natural', 7.00),
            ('Bebidas', 'Milkshake', 10.00),
            ('Bebidas', 'Café gelado', 9.00),
            # Comidas
            ('Comidas', 'Croissant', 8.00),
            ('Comidas', 'Pain au chocolat', 9.00),
            ('Comidas', 'Baguette com queijo e presunto', 10.00),
            ('Comidas', 'Quiche', 12.00),
            ('Comidas', 'Crêpe (doce ou salgado)', 11.00),
            # Doces
            ('Doces', 'Macaron', 6.00),
            ('Doces', 'Madeleine', 7.00),
            ('Doces', 'Éclair', 9.00),
            ('Doces', 'Brownie', 7.00),
            ('Doces', 'Cookie', 5.00),
        ]
        for categoria, nome, preco in cardapio_padrao:
            cursor.execute(
                "INSERT INTO cardapio (categoria, nome, preco) VALUES (%s, %s, %s)",
                (categoria, nome, preco)
            )
        conn.commit()
        print("✅ Cardápio padrão inserido!")
    
except Error as e:
    print(f"❌ Erro de conexão: {e}")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
