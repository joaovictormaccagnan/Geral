from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import mysql.connector
import bcrypt
import json

app = FastAPI(title="🚀 Maison Café API")

# FUNÇÃO DB
def get_db_connection():
    return mysql.connector.connect(
        host='localhost', user='root', password='', database='maison_cafe'
    )

# API ENDPOINTS (SEMPRE PRIMEIRO)
@app.post("/login_admin")
async def login_admin(usuario: str = Form(...), senha: str = Form(...)):
    print(f"👤 LOGIN ADMIN: usuario={usuario}")
    if usuario == "admin" and senha == "senha123":
        print("✅ LOGIN ADMIN OK!")
        return {"sucesso": True, "tipo": "admin", "message": "✅ Bem-vindo(a), Admin!"}
    return {"sucesso": False, "message": "❌ Usuário ou senha inválidos!"}

@app.post("/login_usuario")
async def login_usuario(usuario: str = Form(...), senha: str = Form(...)):
    print(f"👥 LOGIN USUÁRIO: usuario={usuario}")
    if usuario and senha:  # Aceita qualquer usuário e senha
        print("✅ LOGIN USUÁRIO OK!")
        return {"sucesso": True, "tipo": "usuario", "usuario": usuario, "message": f"✅ Bem-vindo(a), {usuario}!"}
    return {"sucesso": False, "message": "❌ Usuário ou senha inválidos!"}

@app.post("/login")
async def login(usuario: str = Form(...), senha: str = Form(...)):
    print(f"🔍 LOGIN: usuario={usuario}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(senha.encode('utf-8'), user['senha'].encode('utf-8')):
            print("✅ LOGIN OK!")
            return {"sucesso": True, "message": f"✅ Bem-vindo(a), {usuario}!"}
        return {"sucesso": False, "message": "❌ Credenciais inválidas!"}
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return {"sucesso": False, "message": "❌ Erro!"}
    finally:
        if conn: conn.close()

@app.post("/registro")
async def registro(usuario: str = Form(...), senha: str = Form(...), email: str = Form(...)):
    print(f"📝 REGISTRO: usuario={usuario}, email={email}")
    conn = None
    try:
        # Criptografar senha
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (usuario, senha, email) VALUES (%s, %s, %s)",
            (usuario, senha_hash, email)
        )
        conn.commit()
        print("✅ USUÁRIO CADASTRADO!")
        return {"sucesso": True, "message": "✅ Cadastro realizado com sucesso!"}
    except mysql.connector.errors.IntegrityError:
        return {"sucesso": False, "message": "❌ Usuário já existe!"}
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return {"sucesso": False, "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

@app.get("/pedidos")
async def listar_pedidos():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pedidos ORDER BY criado_em DESC")
        pedidos = cursor.fetchall()
        return {"pedidos": pedidos}
    except:
        return {"pedidos": []}
    finally:
        if conn: conn.close()

@app.post("/salvar_pedido")
async def salvar_pedido(request: Request):
    conn = None
    try:
        data = await request.json()
        print(f"💾 SALVANDO PEDIDO: usuario={data.get('usuario')}")
        
        itens = data.get('itens', [])
        total = sum(item['preco'] * item['qtd'] for item in itens)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pedidos (usuario, itens, pagamento, total) VALUES (%s, %s, %s, %s)",
            (data['usuario'], json.dumps(itens), data['pagamento'], total)
        )
        conn.commit()
        print("✅ PEDIDO SALVO!")
        return {"sucesso": True, "message": "✅ Pedido salvo com sucesso!"}
    except Exception as e:
        print(f"❌ ERRO ao salvar pedido: {e}")
        return {"sucesso": False, "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

@app.delete("/pedido/{pedido_id}")
async def deletar_pedido(pedido_id: int):
    print(f"🗑️ DELETANDO PEDIDO: id={pedido_id}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pedidos WHERE id = %s", (pedido_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print("✅ PEDIDO DELETADO!")
            return {"sucesso": True, "message": "✅ Pedido deletado com sucesso!"}
        return {"sucesso": False, "message": "❌ Pedido não encontrado!"}
    except Exception as e:
        print(f"❌ ERRO ao deletar pedido: {e}")
        return {"sucesso": False, "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

@app.delete("/limpar_pedidos")
async def limpar_pedidos():
    print(f"🗑️ LIMPANDO TODOS OS PEDIDOS")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pedidos")
        conn.commit()
        print(f"✅ {cursor.rowcount} PEDIDOS DELETADOS!")
        return {"sucesso": True, "mensagem": f"✅ {cursor.rowcount} pedidos deletados com sucesso!"}
    except Exception as e:
        print(f"❌ ERRO ao limpar pedidos: {e}")
        return {"sucesso": False, "mensagem": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

# PÁGINAS HTML (ANTES do StaticFiles)
@app.get("/")
async def home():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>🚀 Maison Café</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; 
               background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        .btn { display: inline-block; padding: 15px 30px; margin: 10px; 
               background: linear-gradient(45deg, #D2B48C, #8B4513); color: white; 
               text-decoration: none; border-radius: 25px; font-weight: bold; }
        h1 { color: #8B4513; font-size: 3rem; }
    </style>
</head>
<body>
    <h1>🍵 Maison Café</h1>
    <h2>✅ Sistema funcionando perfeitamente!</h2>
    <p><strong>🔐 Login:</strong> <code>admin</code> / <code>senha123</code></p>
    <a href="/login.html" class="btn">🔐 Login</a>
    <a href="/loja.html" class="btn">🛒 Loja</a>
    <a href="/docs" class="btn">📚 API Docs</a>
</body>
</html>
    """)

@app.get("/login.html")
async def get_login():
    return FileResponse("login.html")

@app.get("/loja.html")
async def get_loja():
    return FileResponse("loja.html")

@app.get("/relatorio.html")
async def get_relatorio():
    return FileResponse("relatorio.html")

# StaticFiles NO FINAL (só arquivos CSS/JS)
app.mount("/static", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
