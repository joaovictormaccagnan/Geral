from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
import sqlite3
import json
import os

app = FastAPI(title="🍵 Maison Café API", version="1.0.0")

# Arquivo SQLite (cria automaticamente)
DATABASE_FILE = "maison_cafe.db"

# Rotas para servir HTML
@app.get("/login.html")
async def get_login():
    return FileResponse("login.html")

@app.get("/loja.html")
async def get_loja():
    return FileResponse("loja.html")

@app.get("/")
async def root():
    return {
        "🍵 Maison Café": "Online!",
        "Login": "/login.html",
        "Loja": "/loja.html", 
        "Pedidos": "/pedidos",
        "Docs": "/docs"
    }

# LOGIN
@app.post("/login")
async def login(request: Request):
    form = await request.form()
    usuario = form.get("usuario")
    senha = form.get("senha")
    
    print(f"🔐 Login: {usuario}")
    
    sucesso = (usuario == "admin" and senha == "1234")
    
    if sucesso:
        print(f"✅ Login OK: {usuario}")
        return {"message": "Login OK! 🎉", "sucesso": True, "usuario": usuario}
    print(f"❌ Login falhou: {usuario}")
    return {"message": "Usuário ou senha incorretos ❌", "sucesso": False}

# SALVAR PEDIDO (SQLite)
@app.post("/salvar_pedido")
async def salvar_pedido(request: Request):
    try:
        dados = await request.json()
        print("📦 PEDIDO:", dados)
        
        itens = dados['itens']
        pagamento = dados['pagamento']
        usuario = dados.get('usuario')
        total = sum(float(item['preco']) * int(item['qtd']) for item in itens)
        itens_json = json.dumps(itens)
        
        # SQLite - cria tabela se não existir
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT,
                itens TEXT,
                pagamento TEXT,
                total REAL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute(
            "INSERT INTO pedidos (usuario, itens, pagamento, total) VALUES (?, ?, ?, ?)",
            (usuario, itens_json, pagamento, total)
        )
        pedido_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Pedido #{pedido_id} SALVO no SQLite!")
        return {'sucesso': True, 'pedido_id': pedido_id}
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return JSONResponse(status_code=500, content={'sucesso': False, 'mensagem': str(e)})

# LISTAR PEDIDOS
@app.get("/pedidos")
async def listar_pedidos():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pedidos ORDER BY criado_em DESC LIMIT 10")
        pedidos = [{"id": row[0], "usuario": row[1], "itens": row[2], "pagamento": row[3], "total": row[4], "criado_em": row[5]} for row in cursor.fetchall()]
        conn.close()
        print(f"📋 Listando {len(pedidos)} pedidos")
        return {'pedidos': pedidos}
    except Exception as e:
        print(f"❌ Erro listar: {e}")
        return {'pedidos': []}
@app.get("/relatorio.html")
async def get_relatorio():
    return FileResponse("relatorio.html")
# LIMPAR TODOS OS PEDIDOS (cuidado!)
@app.delete("/limpar_pedidos")
async def limpar_pedidos():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pedidos")
        deletados = cursor.rowcount
        conn.commit()
        conn.close()
        print(f"🧹 {deletados} pedidos apagados!")
        return {"mensagem": f"🧹 {deletados} pedidos apagados com sucesso!"}
    except Exception as e:
        print(f"❌ Erro ao limpar: {e}")
        return {"erro": str(e)}



