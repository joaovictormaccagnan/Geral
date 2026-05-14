from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import bcrypt
import json
from chatbot_ia import chatbot

app = FastAPI(title="🚀 Maison Café API")

# ============================================
# CORS - Permitir requisições do frontend
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir de qualquer origem
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, DELETE, etc
    allow_headers=["*"],  # Todos os headers
)

# voce apenas da o caminho para a api (mostra o caminho) e endpoints
# FUNÇÃO DB
def get_db_connection():
    return mysql.connector.connect(
        host='localhost', user='root', password='', database='maison_cafe'
    )

# Função para retornar arquivo sem cache
def get_file_no_cache(file_path: str):
    response = FileResponse(file_path)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

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
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se o usuário existe no banco
        cursor.execute("SELECT usuario, senha FROM usuarios WHERE usuario = %s", (usuario,))
        result = cursor.fetchone()
        
        if result is None:
            print(f"❌ USUÁRIO NÃO ENCONTRADO: {usuario}")
            return {"sucesso": False, "message": "❌ Usuário não encontrado! Registre-se primeiro."}
        
        usuario_db, senha_hash = result
        
        # Verificar senha
        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
            # Registrar login na tabela de logins
            cursor.execute(
                "INSERT INTO logins (usuario) VALUES (%s)",
                (usuario,)
            )
            conn.commit()
            print("✅ LOGIN USUÁRIO OK!")
            return {"sucesso": True, "tipo": "usuario", "usuario": usuario, "message": f"✅ Bem-vindo(a), {usuario}!"}
        else:
            print(f"❌ SENHA INCORRETA: {usuario}")
            return {"sucesso": False, "message": "❌ Senha incorreta!"}
    except Exception as e:
        print(f"❌ ERRO LOGIN USUARIO: {e}")
        return {"sucesso": False, "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

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
async def registro(usuario: str = Form(...), senha: str = Form(...)):
    print(f"📝 REGISTRO: usuario={usuario}")
    conn = None
    try:
        # Criptografar senha
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)",  # ← CORRIGIDO: 2 %s
            (usuario, senha_hash)                                      # ← 2 parâmetros
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

# ENDPOINTS DE CARDÁPIO (ADMIN)
@app.get("/cardapio")
async def listar_cardapio():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cardapio ORDER BY categoria, nome")
        itens = cursor.fetchall()
        return {"sucesso": True, "itens": itens}
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return {"sucesso": False, "itens": []}
    finally:
        if conn: conn.close()

@app.post("/cardapio")
async def adicionar_cardapio(categoria: str = Form(...), nome: str = Form(...), preco: float = Form(...)):
    print(f"➕ ADICIONANDO ITEM: {nome} - R$ {preco}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO cardapio (categoria, nome, preco) VALUES (%s, %s, %s)",
            (categoria, nome, preco)
        )
        conn.commit()
        print("✅ ITEM ADICIONADO!")
        return {"sucesso": True, "message": "✅ Item adicionado com sucesso!"}
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return {"sucesso": False, "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

@app.put("/cardapio/{item_id}")
async def atualizar_cardapio(item_id: int, nome: str = Form(...), preco: float = Form(...)):
    print(f"✏️ ATUALIZANDO ITEM {item_id}: {nome} - R$ {preco}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE cardapio SET nome = %s, preco = %s WHERE id = %s",
            (nome, preco, item_id)
        )
        conn.commit()
        if cursor.rowcount > 0:
            print("✅ ITEM ATUALIZADO!")
            return {"sucesso": True, "message": "✅ Item atualizado com sucesso!"}
        return {"sucesso": False, "message": "❌ Item não encontrado!"}
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return {"sucesso": False, "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

@app.delete("/cardapio/{item_id}")
async def deletar_cardapio(item_id: int):
    print(f"🗑️ DELETANDO ITEM: id={item_id}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cardapio WHERE id = %s", (item_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print("✅ ITEM DELETADO!")
            return {"sucesso": True, "message": "✅ Item deletado com sucesso!"}
        return {"sucesso": False, "message": "❌ Item não encontrado!"}
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return {"sucesso": False, "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

@app.get("/usuarios_login")
async def listar_usuarios_login():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT DISTINCT usuario, COUNT(*) as total_logins, MAX(data_login) as ultimo_login
            FROM logins
            GROUP BY usuario
            ORDER BY ultimo_login DESC
        """)
        usuarios = cursor.fetchall()
        return {"sucesso": True, "usuarios": usuarios}
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return {"sucesso": False, "usuarios": []}
    finally:
        if conn: conn.close()

@app.post("/salvar_pagamento")
async def salvar_pagamento(request: Request):
    conn = None
    try:
        data = await request.json()
        usuario = data.get('usuario')
        metodo = data.get('metodo')
        total = data.get('total')
        nome_titular = data.get('nome_titular')
        cpf = data.get('cpf', '')

        print(f"💳 SALVANDO PAGAMENTO: usuario={usuario}, metodo={metodo}, total=R$ {total}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pagamentos (usuario, metodo, total, nome_titular, cpf) VALUES (%s, %s, %s, %s, %s)",
            (usuario, metodo, total, nome_titular, cpf)
        )
        conn.commit()
        print("✅ PAGAMENTO SALVO!")
        return {"sucesso": True, "message": "✅ Pagamento processado com sucesso!"}
    except Exception as e:
        print(f"❌ ERRO ao salvar pagamento: {e}")
        return {"sucesso": False, "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

# ========== ENDPOINTS DE ESTOQUE (ADMIN) ==========
@app.get("/estoque")
async def listar_estoque():
    """Listar todos os produtos do estoque"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nome, categoria, quantidade, preco_unitario, nivel_minimo, unidade, criado_em
            FROM estoque
            ORDER BY categoria, nome
        """)
        estoque = cursor.fetchall()
        return {"sucesso": True, "estoque": estoque}
    except Exception as e:
        print(f"❌ ERRO ao listar estoque: {e}")
        return {"sucesso": False, "estoque": [], "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

@app.get("/estoque/{item_id}")
async def obter_estoque(item_id: int):
    """Obter detalhes de um produto específico"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nome, categoria, quantidade, preco_unitario, nivel_minimo, unidade, criado_em
            FROM estoque
            WHERE id = %s
        """, (item_id,))
        produto = cursor.fetchone()
        
        if produto:
            return {"sucesso": True, "produto": produto}
        return {"sucesso": False, "message": "❌ Produto não encontrado!"}
    except Exception as e:
        print(f"❌ ERRO ao obter estoque: {e}")
        return {"sucesso": False, "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

@app.post("/estoque")
async def adicionar_estoque(
    nome: str = Form(...),
    categoria: str = Form(...),
    quantidade: int = Form(...),
    preco_unitario: float = Form(...),
    nivel_minimo: int = Form(...),
    unidade: str = Form(...)
):
    """Adicionar novo produto ao estoque"""
    print(f"➕ ADICIONANDO ESTOQUE: {nome} - {quantidade} {unidade}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO estoque (nome, categoria, quantidade, preco_unitario, nivel_minimo, unidade)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, categoria, quantidade, preco_unitario, nivel_minimo, unidade))
        conn.commit()
        print("✅ PRODUTO ADICIONADO AO ESTOQUE!")
        return {"sucesso": True, "message": "✅ Produto adicionado com sucesso!"}
    except mysql.connector.errors.IntegrityError:
        return {"sucesso": False, "message": "❌ Produto já existe!"}
    except Exception as e:
        print(f"❌ ERRO ao adicionar estoque: {e}")
        return {"sucesso": False, "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

@app.put("/estoque/{item_id}")
async def atualizar_estoque(
    item_id: int,
    nome: str = Form(...),
    categoria: str = Form(...),
    quantidade: int = Form(...),
    preco_unitario: float = Form(...),
    nivel_minimo: int = Form(...),
    unidade: str = Form(...)
):
    """Atualizar produto do estoque"""
    print(f"✏️ ATUALIZANDO ESTOQUE {item_id}: {nome}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE estoque
            SET nome = %s, categoria = %s, quantidade = %s, preco_unitario = %s, nivel_minimo = %s, unidade = %s
            WHERE id = %s
        """, (nome, categoria, quantidade, preco_unitario, nivel_minimo, unidade, item_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            print("✅ ESTOQUE ATUALIZADO!")
            return {"sucesso": True, "message": "✅ Produto atualizado com sucesso!"}
        return {"sucesso": False, "message": "❌ Produto não encontrado!"}
    except Exception as e:
        print(f"❌ ERRO ao atualizar estoque: {e}")
        return {"sucesso": False, "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

@app.delete("/estoque/{item_id}")
async def deletar_estoque(item_id: int):
    """Deletar produto do estoque"""
    print(f"🗑️ DELETANDO ESTOQUE: id={item_id}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM estoque WHERE id = %s", (item_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print("✅ ESTOQUE DELETADO!")
            return {"sucesso": True, "message": "✅ Produto deletado com sucesso!"}
        return {"sucesso": False, "message": "❌ Produto não encontrado!"}
    except Exception as e:
        print(f"❌ ERRO ao deletar estoque: {e}")
        return {"sucesso": False, "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

@app.post("/estoque/{item_id}/reabastecimento")
async def reabastecimento(item_id: int, request: Request):
    """Reabastecimento de produto (aumentar quantidade e atualizar preço)"""
    conn = None
    try:
        data = await request.json()
        quantidade_adicionar = data.get('quantidade_adicionar', 0)
        preco_reabastecimento = data.get('preco_reabastecimento', 0)
        
        print(f"📦 REABASTECIMENTO: id={item_id}, qtd={quantidade_adicionar}, preco=R$ {preco_reabastecimento}")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Buscar produto atual
        cursor.execute("SELECT quantidade, preco_unitario FROM estoque WHERE id = %s", (item_id,))
        produto = cursor.fetchone()
        
        if not produto:
            return {"sucesso": False, "message": "❌ Produto não encontrado!"}
        
        nova_quantidade = produto['quantidade'] + quantidade_adicionar
        custo_total = quantidade_adicionar * preco_reabastecimento
        
        # Atualizar estoque
        cursor.execute("""
            UPDATE estoque
            SET quantidade = %s, preco_unitario = %s
            WHERE id = %s
        """, (nova_quantidade, preco_reabastecimento, item_id))
        conn.commit()
        
        print("✅ REABASTECIMENTO REALIZADO!")
        return {
            "sucesso": True,
            "message": f"✅ Reabastecimento realizado! Custo total: R$ {custo_total:.2f}",
            "quantidade_nova": nova_quantidade,
            "custo_total": custo_total
        }
    except Exception as e:
        print(f"❌ ERRO ao fazer reabastecimento: {e}")
        return {"sucesso": False, "message": f"❌ Erro: {str(e)}"}
    finally:
        if conn: conn.close()

# ========== ENDPOINT DE DASHBOARD ==========
@app.get("/dashboard")
async def dashboard():
    """Retorna dados para o dashboard de vendas"""
    conn = None
    try:
        from datetime import datetime, timedelta
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Data de hoje
        hoje = datetime.now().date()
        ontem = hoje - timedelta(days=1)
        sete_dias_atras = hoje - timedelta(days=7)
        
        # 1. Total de pedidos do dia
        cursor.execute("""
            SELECT COUNT(*) as total FROM pedidos
            WHERE DATE(criado_em) = %s
        """, (hoje,))
        total_pedidos_hoje = cursor.fetchone()['total']
        
        # 2. Faturamento do dia
        cursor.execute("""
            SELECT SUM(total) as faturamento FROM pedidos
            WHERE DATE(criado_em) = %s
        """, (hoje,))
        resultado = cursor.fetchone()
        faturamento_hoje = float(resultado['faturamento'] or 0)
        
        # 3. Ticket médio do dia
        ticket_medio = faturamento_hoje / total_pedidos_hoje if total_pedidos_hoje > 0 else 0
        
        # 4. Item mais vendido do dia
        cursor.execute("""
            SELECT itens FROM pedidos
            WHERE DATE(criado_em) = %s
        """, (hoje,))
        pedidos_hoje = cursor.fetchall()
        
        item_mais_vendido = "N/A"
        if pedidos_hoje:
            item_count = {}
            for pedido in pedidos_hoje:
                itens = json.loads(pedido['itens'])
                for item in itens:
                    nome = item['nome']
                    qtd = item['qtd']
                    item_count[nome] = item_count.get(nome, 0) + qtd
            
            if item_count:
                item_mais_vendido = max(item_count, key=item_count.get)
        
        # 5. Faturamento dos últimos 7 dias
        cursor.execute("""
            SELECT DATE(criado_em) as data, SUM(total) as total
            FROM pedidos
            WHERE DATE(criado_em) >= %s
            GROUP BY DATE(criado_em)
            ORDER BY data ASC
        """, (sete_dias_atras,))
        
        faturamento_7dias_raw = cursor.fetchall()
        faturamento_7dias = []
        
        # Preencher todos os dias (incluindo dias sem vendas)
        data_atual = sete_dias_atras
        faturamento_dict = {str(row['data']): float(row['total']) for row in faturamento_7dias_raw}
        
        for i in range(7):
            data_str = str(data_atual)
            faturamento_7dias.append({
                'data': data_str,
                'total': faturamento_dict.get(data_str, 0)
            })
            data_atual += timedelta(days=1)
        
        # 6. Pedidos por forma de pagamento
        cursor.execute("""
            SELECT pagamento, COUNT(*) as quantidade
            FROM pedidos
            WHERE DATE(criado_em) = %s
            GROUP BY pagamento
        """, (hoje,))
        
        pedidos_por_pagamento_raw = cursor.fetchall()
        pedidos_por_pagamento = [
            {'metodo': row['pagamento'], 'quantidade': row['quantidade']}
            for row in pedidos_por_pagamento_raw
        ]
        
        return {
            "sucesso": True,
            "total_pedidos_hoje": total_pedidos_hoje,
            "faturamento_hoje": round(faturamento_hoje, 2),
            "ticket_medio": round(ticket_medio, 2),
            "item_mais_vendido": item_mais_vendido,
            "faturamento_7dias": faturamento_7dias,
            "pedidos_por_pagamento": pedidos_por_pagamento
        }
    except Exception as e:
        print(f"❌ ERRO ao gerar dashboard: {e}")
        return {
            "sucesso": False,
            "erro": str(e),
            "total_pedidos_hoje": 0,
            "faturamento_hoje": 0,
            "ticket_medio": 0,
            "item_mais_vendido": "N/A",
            "faturamento_7dias": [],
            "pedidos_por_pagamento": []
        }
    finally:
        if conn: conn.close()

# ============================================
# ENDPOINTS DO CHATBOT IA 🤖
# ============================================
@app.post("/chat")
async def chat(request: Request):
    """Endpoint do Chatbot IA - Responde perguntas sobre receitas e site"""
    try:
        data = await request.json()
        mensagem = data.get('mensagem', '').strip()
        usuario_id = data.get('usuario_id', 'guest')
        
        if not mensagem:
            return {"erro": "Mensagem vazia"}
        
        print(f"💬 CHATBOT: usuario={usuario_id}, mensagem={mensagem[:50]}")
        
        # Processar mensagem com chatbot
        resposta = chatbot.processar_entrada(mensagem, usuario_id)
        
        return {
            "sucesso": True,
            "resposta": resposta['resposta'],
            "confianca": resposta['confianca'],
            "sugestoes": resposta['sugestoes'],
            "tipo": resposta['tipo']
        }
    except Exception as e:
        print(f"❌ ERRO CHATBOT: {e}")
        return {"sucesso": False, "erro": str(e)}

@app.get("/chat/historico/{usuario_id}")
async def obter_historico(usuario_id: str):
    """Obtém histórico de conversas do usuário"""
    try:
        historico = chatbot.obter_historico(usuario_id)
        return {"sucesso": True, "historico": historico}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

@app.get("/chat/receitas")
async def listar_receitas():
    """Lista todas as receitas disponíveis"""
    from chatbot_ia import KNOWLEDGE_BASE
    try:
        receitas = KNOWLEDGE_BASE['receitas']
        return {"sucesso": True, "receitas": receitas, "total": len(receitas)}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

@app.get("/chat/faqs")
async def listar_faqs():
    """Lista todos os FAQs"""
    from chatbot_ia import KNOWLEDGE_BASE
    try:
        faqs = KNOWLEDGE_BASE['faqs']
        return {"sucesso": True, "faqs": faqs, "total": len(faqs)}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

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
    <a href="/index.html" class="btn">🔐 Login</a>
    <a href="/docs" class="btn">📚 API Docs</a>
</body>
</html>
    """)

@app.get("/index.html")
async def get_index():
    return get_file_no_cache("index.html")

@app.get("/loja.html")
async def get_loja():
    return get_file_no_cache("loja.html")

@app.get("/pagamento.html")
async def get_pagamento():
    return get_file_no_cache("pagamento.html")

@app.get("/admin.html")
async def get_admin():
    return get_file_no_cache("admin.html")

@app.get("/relatorio.html")
async def get_relatorio():
    return get_file_no_cache("relatorio.html")

@app.get("/estoque.html")
async def get_estoque():
    return get_file_no_cache("estoque.html")

@app.get("/chatbot_widget.js")
async def get_chatbot_widget():
    return get_file_no_cache("chatbot_widget.js")

# StaticFiles NO FINAL (só arquivos CSS/JS)
app.mount("/static", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
