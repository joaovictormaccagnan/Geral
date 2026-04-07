# 🍵 Documentação Completa - Maison Café

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Arquivos Backend](#arquivos-backend)
4. [Arquivos Frontend](#arquivos-frontend)
5. [Banco de Dados](#banco-de-dados)
6. [Fluxo de Funcionamento](#fluxo-de-funcionamento)
7. [Como Executar](#como-executar)

---

## 🎯 Visão Geral

O **Maison Café** é um sistema web completo de gerenciamento de pedidos de um café virtual, com:
- ✅ Autenticação com 2 níveis (Admin e Usuário)
- ✅ Cardápio com múltiplas categorias
- ✅ Carrinho de compras funcionando
- ✅ Sistema de pedidos com banco de dados MySQL
- ✅ Relatório de vendas (apenas Admin)
- ✅ Gerenciamento de pedidos (deletar individual/todos)

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                      NAVEGADOR                          │
│  (login.html → loja.html / relatorio.html)              │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP/HTTPS
                     ↓
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Server                        │
│  (api_maison.py - Porta 8000)                           │
│  • Login Admin/Usuário                                  │
│  • Salvar/Listar/Deletar Pedidos                        │
│  • Servir HTML estático                                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Conexão TCP
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  MySQL 8.0 Database                     │
│  • Tabela: usuarios (login)                             │
│  • Tabela: pedidos (vendas)                             │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Arquivos Backend

### 1️⃣ **api_maison.py** - API Principal
**Função:** Servidor FastAPI que gerencia toda a lógica do sistema

**Componentes principais:**

#### Importações
```python
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import mysql.connector
import bcrypt
import json
```

#### Conexão com Banco (Função auxiliar)
```python
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='maison_cafe'
    )
```

#### Endpoints (Rotas de API):

| Rota | Método | Função |
|------|--------|--------|
| `/login_admin` | POST | Login exclusivo: admin/senha123 |
| `/login_usuario` | POST | Login aberto: qualquer usuário |
| `/login` | POST | Login por banco de dados |
| `/registro` | POST | Registrar novo usuário |
| `/pedidos` | GET | Listar todos os pedidos |
| `/salvar_pedido` | POST | Salvar novo pedido |
| `/pedido/{id}` | DELETE | Deletar pedido específico |
| `/limpar_pedidos` | DELETE | Deletar todos os pedidos |
| `/` | GET | Página inicial |
| `/login.html` | GET | Servir login.html |
| `/loja.html` | GET | Servir loja.html |
| `/relatorio.html` | GET | Servir relatorio.html |

**Fluxo do Login Admin:**
```
usuário digita admin/senha123
         ↓
POST /login_admin
         ↓
Valida credenciais
         ↓
Retorna {"sucesso": true, "tipo": "admin"}
         ↓
JavaScript salva em sessionStorage
         ↓
Redireciona para relatorio.html
```

**Fluxo de Salvar Pedido:**
```
Cliente clica "Finalizar Compra"
         ↓
JavaScript envia POST /salvar_pedido
         ↓
API recebe: {usuario, itens[], pagamento}
         ↓
Calcula total: sum(preco * qtd)
         ↓
Salva no MySQL: INSERT INTO pedidos
         ↓
Retorna {"sucesso": true}
         ↓
JavaScript exibe confirmação
```

---

### 2️⃣ **criar_tabela.py** - Inicialização do Banco
**Função:** Script Python que cria as tabelas no MySQL

```python
# Cria tabela usuários
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

# Cria tabela pedidos
CREATE TABLE pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100),
    itens JSON NOT NULL,
    pagamento VARCHAR(20) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario) REFERENCES usuarios(usuario)
)
```

**Para executar:**
```bash
python criar_tabela.py
```

---

### 3️⃣ **maison_cafe.sql** - Script SQL Alternativo
**Função:** Arquivo SQL para criar banco via MySQL diretamente

**Para executar:**
```bash
mysql -u root < maison_cafe.sql
```

---

### 4️⃣ **requirements.txt** - Dependências Python
```
fastapi==0.115.0              # Framework web
uvicorn[standard]==0.30.6    # Servidor ASGI
mysql-connector-python==9.1.0 # Conexão MySQL
bcrypt                         # Criptografia de senhas
```

**Para instalar:**
```bash
pip install -r requirements.txt
```

---

## 🎨 Arquivos Frontend

### 1️⃣ **login.html** - Página de Autenticação

**Estrutura HTML:**
```html
<div class="container">
    <div class="tabs">
        <button onclick="mudarAba('admin')">👨‍💼 Admin</button>
        <button onclick="mudarAba('usuario')">👤 Usuário</button>
    </div>
    
    <!-- ABA 1: Login Admin -->
    <div id="admin">
        <input id="admin_user" value="admin">
        <input type="password" id="admin_pass" value="senha123">
        <button onclick="loginAdmin(event)">Entrar como Admin</button>
    </div>
    
    <!-- ABA 2: Login Usuário -->
    <div id="usuario">
        <input id="user_user" placeholder="Qualquer usuário">
        <input type="password" id="user_pass" placeholder="Qualquer senha">
        <button onclick="loginUsuario(event)">Entrar como Usuário</button>
    </div>
</div>
```

**Funções JavaScript:**

```javascript
// Alterna entre abas
function mudarAba(aba) {
    // Esconde todos
    document.getElementById('admin').classList.remove('active');
    document.getElementById('usuario').classList.remove('active');
    // Mostra selecionado
    document.getElementById(aba).classList.add('active');
}

// Login Admin
async function loginAdmin(e) {
    const usuario = document.getElementById('admin_user').value;
    const senha = document.getElementById('admin_pass').value;
    
    const res = await fetch('/login_admin', {
        method: 'POST',
        body: `usuario=${usuario}&senha=${senha}`
    });
    
    const data = await res.json();
    if (data.sucesso) {
        sessionStorage.setItem('tipoLogin', 'admin');
        window.location.href = 'relatorio.html';
    }
}

// Login Usuário (similar)
```

**Estilos CSS:**
- Interface com 2 abas deslizantes
- Gradiente marrom/bege (tema café)
- Responsivo para mobile
- Animações suaves

---

### 2️⃣ **loja.html** - Página de Compras

**Estrutura:**
```
┌─────────────────────────────────────────┐
│  HEADER (navegação + carrinho)          │
├─────────────────────────────────────────┤
│                                         │
│  Seção 1: Cafés (items + preços)       │
│  Seção 2: Bebidas Quentes              │
│  Seção 3: Bebidas Frias                │
│  Seção 4: Doces                        │
│                                         │
├─────────────────────────────────────────┤
│  CARRINHO LATERAL                       │
│  • Lista itens selecionados            │
│  • Total da compra                     │
│  • Botão Finalizar                     │
└─────────────────────────────────────────┘
```

**Cardápio e Dados:**
```javascript
// Exemplo de cardápio
const menu = [
    { 
        categoria: "Cafés",
        itens: [
            {nome: "Café Expresso", preco: 5.50},
            {nome: "Cappuccino", preco: 8.00},
            {nome: "Latte", preco: 9.50}
        ]
    },
    // ... mais categorias
];
```

**Funções Principais:**

```javascript
// Adicionar ao carrinho
function adicionarCarrinho(nome, preco) {
    const existente = carrinho.find(item => item.nome === nome);
    if (existente) {
        existente.qtd++;
    } else {
        carrinho.push({nome, preco, qtd: 1});
    }
    atualizarCarrinhoVisual();
}

// Atualizar visual do carrinho
function atualizarCarrinhoVisual() {
    let html = '';
    let total = 0;
    carrinho.forEach(item => {
        html += `<li>${item.nome} x${item.qtd} - R$ ${item.preco}</li>`;
        total += item.preco * item.qtd;
    });
    document.getElementById('carrinho').innerHTML = html;
    document.getElementById('total').innerText = total.toFixed(2);
}

// Finalizar compra
async function finalizarCompra() {
    const usuario = sessionStorage.getItem('usuarioLogado');
    const payload = {
        usuario,
        itens: carrinho,
        pagamento: document.getElementById('pagamento').value
    };
    
    const res = await fetch('/salvar_pedido', {
        method: 'POST',
        body: JSON.stringify(payload)
    });
    
    const data = await res.json();
    if (data.sucesso) {
        alert('✅ Pedido realizado!');
        carrinho = [];
        atualizarCarrinhoVisual();
    }
}
```

**Proteção contra Admin:**
```javascript
const tipoLogin = sessionStorage.getItem('tipoLogin');
if (tipoLogin === 'admin') {
    alert('Admin detectado! Redirecionando para relatório...');
    window.location.href = 'relatorio.html';
}
```

---

### 3️⃣ **relatorio.html** - Página de Relatório (Admin)

**Estrutura:**
```
┌──────────────────────────┐
│  HEADER COM ESTATÍSTICAS │
│  • Total de Pedidos: 5   │
│  • Faturamento: R$250    │
│  • Botões: Atualizar     │
│            Limpar Todos  │
│            Sair          │
├──────────────────────────┤
│                          │
│ TABELA DE PEDIDOS        │
│ ID | Usuário | Items    │
│ 1  | João    | 2 Cafés  │
│ 2  | Maria   | 1 Bolo   │
│                          │
└──────────────────────────┘
```

**Proteção (apenas Admin):**
```javascript
window.addEventListener('load', function() {
    const tipoLogin = sessionStorage.getItem('tipoLogin');
    if (tipoLogin !== 'admin') {
        alert('❌ Acesso negado! Apenas ADMIN pode ver.');
        window.location.href = 'login.html';
    }
});
```

**Carregar Pedidos:**
```javascript
async function carregarPedidos() {
    const res = await fetch('/pedidos');
    const data = await res.json();
    
    let totalGeral = 0;
    let html = '';
    
    data.pedidos.forEach(pedido => {
        const itens = JSON.parse(pedido.itens);
        const itensHtml = itens
            .map(i => `${i.nome} (x${i.qtd})`)
            .join(', ');
        
        totalGeral += pedido.total;
        html += `
            <tr>
                <td>${pedido.id}</td>
                <td>${pedido.usuario}</td>
                <td>${itensHtml}</td>
                <td>R$ ${pedido.total.toFixed(2)}</td>
                <td>
                    <button onclick="deletarPedido(${pedido.id})">
                        🗑️ Deletar
                    </button>
                </td>
            </tr>
        `;
    });
    
    document.getElementById('listaPedidos').innerHTML = html;
    document.getElementById('totalGeralDiv').innerText = 
        `R$ ${totalGeral.toFixed(2)}`;
}
```

**Deletar Pedido:**
```javascript
async function deletarPedido(pedidoId) {
    if (confirm('Tem certeza?')) {
        const res = await fetch(`/pedido/${pedidoId}`, {
            method: 'DELETE'
        });
        const data = await res.json();
        if (data.sucesso) {
            carregarPedidos(); // recarrega tabela
        }
    }
}
```

---

## 💾 Banco de Dados

### Tabela: usuarios
```sql
┌────────────────────────────────────────┐
│             USUARIOS                   │
├────────────────────────────────────────┤
│ id          | INT PRIMARY KEY          │
│ usuario     | VARCHAR(100) UNIQUE      │
│ senha       | VARCHAR(255) [bcrypt]    │
│ email       | VARCHAR(100)             │
│ criado_em   | TIMESTAMP                │
└────────────────────────────────────────┘
```

**Exemplo:**
```
id=1, usuario="admin", senha="$2b$12$...", email="admin@maison.com"
```

### Tabela: pedidos
```sql
┌────────────────────────────────────────┐
│             PEDIDOS                    │
├────────────────────────────────────────┤
│ id          | INT PRIMARY KEY          │
│ usuario     | VARCHAR(100) FK          │
│ itens       | JSON                     │
│ pagamento   | VARCHAR(20)              │
│ total       | DECIMAL(10,2)            │
│ criado_em   | TIMESTAMP                │
└────────────────────────────────────────┘
```

**Exemplo JSON itens:**
```json
[
  {"nome": "Cappuccino", "preco": 8.00, "qtd": 2},
  {"nome": "Bolo de Chocolate", "preco": 12.00, "qtd": 1}
]
```

---

## 🔄 Fluxo de Funcionamento

### 1️⃣ **Primeiro Acesso**
```
Usuário acessa localhost:8000
         ↓
Abre home page com 3 botões
         ↓
Clica "Login" → vai para login.html
```

### 2️⃣ **Login Admin**
```
login.html (aba Admin)
         ↓
Digita: admin / senha123
         ↓
POST /login_admin
         ↓
Valida credenciais (usuario=="admin" AND senha=="senha123")
         ↓
Retorna {"sucesso": true, "tipo": "admin"}
         ↓
sessionStorage.tipoLogin = "admin"
         ↓
Redireciona para relatorio.html
         ↓
relatorio.html verifica: if (tipoLogin !== 'admin') redirect
         ↓
Mostra tabela de pedidos com relatório
```

### 3️⃣ **Login Usuário Normal**
```
login.html (aba Usuário)
         ↓
Digita: qualquer_user / qualquer_pass
         ↓
POST /login_usuario
         ↓
Valida: if (usuario && senha) ✓
         ↓
Retorna {"sucesso": true, "tipo": "usuario"}
         ↓
sessionStorage.tipoLogin = "usuario"
         ↓
Redireciona para loja.html
         ↓
loja.html verifica: if (tipoLogin === 'admin') redirect
         ↓
Mostra cardápio com opção de compra
```

### 4️⃣ **Fazer Compra**
```
Usuário seleciona itens no cardápio
         ↓
Clica "Adicionar ao Carrinho"
         ↓
JavaScript adiciona a carrinho[] local
         ↓
Carrinho lateral atualiza com itens
         ↓
Usuário seleciona forma de pagamento
         ↓
Clica "Finalizar Compra"
         ↓
JavaScript valida carrinho
         ↓
POST /salvar_pedido com {usuario, itens[], pagamento}
         ↓
API calcula total: sum(preco * qtd)
         ↓
INSERT INTO pedidos (usuario, itens_json, pagamento, total)
         ↓
Retorna {"sucesso": true}
         ↓
Alerta "Pedido realizado!"
         ↓
Carrinho limpo
```

### 5️⃣ **Admin Visualiza Pedidos**
```
Admin acessa relatorio.html
         ↓
JavaScript carrega GET /pedidos
         ↓
API consulta: SELECT * FROM pedidos
         ↓
Retorna array com todos os pedidos
         ↓
JavaScript monta tabela HTML
         ↓
Exibe: ID | usuário | itens | total | data
```

### 6️⃣ **Admin Deleta Pedido**
```
Admin clica 🗑️ em um pedido
         ↓
Confirma: "Tem certeza?"
         ↓
DELETE /pedido/{id}
         ↓
API executa: DELETE FROM pedidos WHERE id=X
         ↓
Confirma: {"sucesso": true}
         ↓
Tabela recarrega automaticamente
```

---

## 🚀 Como Executar

### Passo 1: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 2: Criar Banco de Dados
```bash
# Opção A: Python
python criar_tabela.py

# Opção B: MySQL CLI
mysql -u root < maison_cafe.sql
```

### Passo 3: Iniciar API
```bash
uvicorn api_maison:app --reload
```

Saída esperada:
```
Uvicorn running on http://127.0.0.1:8000
```

### Passo 4: Acessar no Navegador
```
http://127.0.0.1:8000
```

---

## 🔐 Segurança

| Aspecto | Implementação |
|--------|---------------|
| Senhas | Criptografadas com bcrypt |
| Admin | Único usuário fixo: admin/senha123 |
| Sessão | Armazenada em sessionStorage |
| SQL Injection | Parametrized queries com %s |
| CORS | Aberto (desenvolvimento) |

---

## 📊 Resumo Técnico

| Item | Tecnologia |
|------|-----------|
| Backend | Python FastAPI |
| Frontend | HTML/CSS/JavaScript |
| Database | MySQL 8.0 |
| Autenticação | Bcrypt + SessionStorage |
| API | RESTful |
| Servidor | Uvicorn ASGI |

---

## 🎓 Conceitos de Programação Utilizados

✅ **Backend:**
- Async/Await com FastAPI
- Rotas POST, GET, DELETE
- Conexão com banco de dados
- Criptografia de senhas
- Tratamento de exceções
- JSON

✅ **Frontend:**
- Manipulação do DOM
- Fetch API para requisições
- SessionStorage para dados da sessão
- Event listeners
- CSS Flexbox/Grid
- Validações de formulário

✅ **Database:**
- SQL CREATE TABLE
- INSERT, SELECT, DELETE
- Foreign keys
- Índices para performance
- TIMESTAMP automático

---

## 📝 Possíveis Melhorias

1. **Autenticação:** Implementar JWT tokens
2. **Frontend:** React ou Vue.js
3. **Validações:** Mais validações backend
4. **UI/UX:** Dark mode, mais animações
5. **Deploy:** Docker + Vercel/Heroku
6. **Backup:** Sistema automático de backup
7. **Notificações:** Email confirmação pedido
8. **Relatórios:** Gráficos e exportar PDF

---

**Documentação criada em:** 30/03/2026  
**Versão:** 1.0
