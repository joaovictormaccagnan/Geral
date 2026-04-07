import mysql.connector
import bcrypt

print("🔧 MUDAR LOGIN DO SISTEMA MAISON CAFÉ")
print("-" * 40)

# 👤 DIGITE AQUI SUAS NOVAS CREDENCIAIS
novo_usuario = input("👤 Novo usuário: ")
nova_senha = input("🔑 Nova senha: ")  # ← SIMPLES assim!

# Criptografa senha
senha_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()

try:
    # Conecta no banco
    conn = mysql.connector.connect(
        host='localhost', 
        user='root', 
        password='', 
        database='maison_cafe'
    )
    cursor = conn.cursor()
    
    # ATUALIZA o usuário existente
    cursor.execute(
        "UPDATE usuarios SET usuario = %s, senha = %s WHERE id = 1",
        (novo_usuario, senha_hash)
    )
    cursor.execute("""
    ALTER TABLE usuarios DROP COLUMN email
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n✅ ✅ LOGIN ALTERADO!")
    print(f"👤 USUÁRIO: '{novo_usuario}'")
    print(f"🔑 SENHA: '{nova_senha}'")
    print("🌐 Teste: http://127.0.0.1:8000/login.html")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    print("🔧 1. Inicie MySQL: net start MySQL")
    print("🔧 2. Execute: python setup.py")
