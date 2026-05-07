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
    
    # Criar tabela de ESTOQUE (Admin)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100) UNIQUE NOT NULL,
        categoria VARCHAR(50) NOT NULL,
        quantidade INT NOT NULL DEFAULT 0,
        preco_unitario DECIMAL(10,2) NOT NULL,
        nivel_minimo INT NOT NULL DEFAULT 5,
        unidade VARCHAR(20) NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    print("✅ Tabela 'estoque' criada com sucesso!")
    
    # Inserir estoque padrão se ainda não existir
    cursor.execute("SELECT COUNT(*) as count FROM estoque")
    result = cursor.fetchone()
    count = result[0] if isinstance(result, tuple) else result['count']
    if count == 0:
        estoque_padrao = [
            # Bebidas
            ('Bebidas', 'Café em grãos - Arábica Premium', 50, 45.00, 10, 'kg'),
            ('Bebidas', 'Café em grãos - Robusta', 30, 28.00, 10, 'kg'),
            ('Bebidas', 'Leite Integral', 100, 5.50, 20, 'L'),
            ('Bebidas', 'Leite Desnatado', 50, 4.80, 10, 'L'),
            ('Bebidas', 'Chocolate em pó', 15, 25.00, 3, 'kg'),
            # Alimentos
            ('Alimentos', 'Pão Francês Congelado', 200, 0.80, 50, 'un'),
            ('Alimentos', 'Croissant Congelado', 150, 1.50, 30, 'un'),
            ('Alimentos', 'Pain au Chocolat', 100, 2.00, 20, 'un'),
            ('Alimentos', 'Ovos Grandes', 360, 0.50, 100, 'un'),
            ('Alimentos', 'Farinha de Trigo', 20, 35.00, 5, 'kg'),
            ('Alimentos', 'Açúcar Cristal', 15, 4.50, 5, 'kg'),
            ('Alimentos', 'Sal Refinado', 5, 3.00, 2, 'kg'),
            ('Alimentos', 'Manteiga', 20, 15.00, 5, 'kg'),
            # Acessórios
            ('Acessórios', 'Xícara de Porcelana', 100, 8.00, 20, 'un'),
            ('Acessórios', 'Colher de Café', 50, 2.00, 10, 'un'),
            ('Acessórios', 'Guardanapo', 500, 0.05, 200, 'un'),
            ('Acessórios', 'Caneca Térmica', 30, 18.00, 10, 'un'),
        ]
        for categoria, nome, qtd, preco, minimo, unidade in estoque_padrao:
            cursor.execute(
                "INSERT INTO estoque (categoria, nome, quantidade, preco_unitario, nivel_minimo, unidade) VALUES (%s, %s, %s, %s, %s, %s)",
                (categoria, nome, qtd, preco, minimo, unidade)
            )
        conn.commit()
        print("✅ Estoque padrão inserido!")
    
    # Criar tabela de pagamentos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pagamentos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario VARCHAR(100),
        metodo VARCHAR(20) NOT NULL,
        total DECIMAL(10,2) NOT NULL,
        nome_titular VARCHAR(100) NOT NULL,
        cpf VARCHAR(11),
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario) REFERENCES usuarios(usuario)
    )
    """)
    conn.commit()
    print("✅ Tabela 'pagamentos' criada com sucesso!")
    
except Error as e:
    print(f"❌ Erro de conexão: {e}")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
