# 🤖 Chatbot IA Maison Café - Documentação Completa

## 📋 Visão Geral

O **Chatbot IA Maison Café** é um assistente inteligente autônomo que responde dúvidas sobre:

- ☕ **Receitas** - Instruções passo a passo para preparar bebidas
- ❓ **FAQs** - Respostas sobre pedidos, entrega, pagamento e site
- 🛒 **Pedidos** - Ajuda para fazer compras
- 📞 **Suporte** - Informações gerais e contato

## 🎯 Funcionalidades

### Principais

✅ **Chatbot Conversacional** - Interface limpa e intuitiva
✅ **Processamento de Linguagem Natural** - Entende variações de perguntas
✅ **Base de Conhecimento Dinâmica** - FAQs, receitas e informações
✅ **Histórico de Conversas** - Rastreia toda interação do usuário
✅ **Sugestões Inteligentes** - Próximas perguntas recomendadas
✅ **Indicador de Confiança** - Mostra qualidade da resposta
✅ **Totalmente Responsivo** - Funciona em desktop, tablet e mobile
✅ **Dark Mode** - Suporta modo escuro automático
✅ **Sem Dependências Externas** - Usa apenas JavaScript puro

## 🏗️ Arquitetura

### Backend (Python + FastAPI)

```
API Endpoints:
├── POST /chat              - Processa mensagem do usuário
├── GET  /chat/historico/:id - Obtém histórico de conversas
├── GET  /chat/receitas      - Lista todas as receitas
└── GET  /chat/faqs          - Lista todos os FAQs
```

**Arquivo:** `chatbot_ia.py`
- Classe `ChatbotIA` - Lógica principal
- `KNOWLEDGE_BASE` - Base de conhecimento (receitas + FAQs)

**Integração na API:** `api_maison.py`
- Import: `from chatbot_ia import chatbot`
- Endpoints registrados automaticamente

### Frontend (JavaScript)

```
Arquivo: chatbot_widget.js
├── Class ChatbotWidget
│   ├── init()              - Inicialização
│   ├── injetarEstilos()    - CSS do widget
│   ├── criarWidget()       - Cria elementos HTML
│   ├── configurarEventos() - Event listeners
│   ├── enviarMensagem()    - Processa entrada
│   ├── enviarParaBotIA()   - Comunica com backend
│   └── exibirMensagem()    - Renderiza resposta
└── Auto-inicializa quando página carrega
```

**Integração nos HTMLs:**
```html
<script src="chatbot_widget.js"></script>
```

## 🚀 Como Usar

### 1. **Iniciar o Sistema**

```bash
# Terminal 1 - Ativar ambiente virtual
cd c:\Users\aluno\Desktop\Pasta_Principal
venv\Scripts\activate

# Terminal 2 - Iniciar API
python main.py
# ou
uvicorn api_maison:app --reload --host 127.0.0.1 --port 8000
```

### 2. **Acessar o Chatbot**

- ✅ Abrir qualquer página HTML (index.html, loja.html, etc.)
- ✅ Clicar no botão ☕ flutuante no canto inferior direito
- ✅ Digitar sua pergunta

### 3. **Exemplos de Perguntas**

#### Receitas
- "Como faço um cappuccino?"
- "Ingredientes do mocha"
- "Receita de café com leite"

#### FAQs
- "Qual é o tempo de entrega?"
- "Como faço um pedido?"
- "Vocês aceitam PIX?"
- "Qual o horário de funcionamento?"

#### Cardápio
- "O que vocês vendem?"
- "Têm opções veganas?"
- "Vocês têm café descafeinado?"

#### Pedidos
- "Como fazer um pedido?"
- "Como pagar?"
- "Posso cancelar um pedido?"

## 📖 Base de Conhecimento

### Receitas Incluídas

1. **Café Expresso** - Rápido e clássico
2. **Cappuccino** - Café com leite e espuma
3. **Café com Leite** - Tradição brasileira
4. **Mocha** - Café com chocolate
5. **Café Gelado** - Refrescante

### FAQs Inclusos

- Como fazer um pedido?
- Tempo de entrega
- Horário de funcionamento
- Formas de pagamento
- Cancelamento de pedidos
- Opções descafeinadas
- Opções veganas
- Como rastrear pedido

## 🔧 Personalização

### Adicionar Novas Receitas

Edite `chatbot_ia.py` na seção `KNOWLEDGE_BASE`:

```python
KNOWLEDGE_BASE = {
    "receitas": [
        {
            "nome": "Novo Café",
            "ingredientes": ["ingredient1", "ingredient2"],
            "preparo": "Descrição do modo de preparo",
            "tempo": "X minutos",
            "dificuldade": "Fácil"
        }
    ]
}
```

### Adicionar Novos FAQs

```python
"faqs": [
    {
        "pergunta": "Sua pergunta?",
        "resposta": "Sua resposta aqui"
    }
]
```

### Personalizar Estilos

Edite `chatbot_widget.js` na função `injetarEstilos()`:

```javascript
// Cores do widget
background: linear-gradient(135deg, #6F4E37 0%, #8B4513 100%);
```

### Configurar URL da API

```javascript
new ChatbotWidget({
    apiBaseUrl: 'http://seu-servidor.com',
    usuarioId: 'usuario@email.com'
});
```

## 🧠 Como Funciona a IA

### 1. Análise de Entrada
- Normaliza texto (minúsculas)
- Remove espaços extras
- Processa intenção

### 2. Busca de Correspondência
- Verifica keywords (receita, pedido, etc)
- Busca em FAQs por similaridade
- Usa algoritmo **Jaccard** para matching

### 3. Geração de Resposta
- Retorna resposta mais relevante
- Calcula confiança (0-100%)
- Gera sugestões de próximas perguntas

### 4. Histórico
- Armazena todas as mensagens
- Permite rastreamento por usuário
- Disponível via API `/chat/historico/:id`

## 📊 API Reference

### POST /chat

**Request:**
```json
{
    "mensagem": "Como fazer um cappuccino?",
    "usuario_id": "usuario@email.com"
}
```

**Response:**
```json
{
    "sucesso": true,
    "resposta": "🍵 **Cappuccino**...",
    "confianca": 85,
    "sugestoes": ["Outra receita", "Ver cardápio"],
    "tipo": "resposta_normal"
}
```

### GET /chat/historico/:usuario_id

**Response:**
```json
{
    "sucesso": true,
    "historico": [
        {
            "usuario": "guest",
            "mensagem": "Oi",
            "tipo": "pergunta"
        },
        {
            "usuario": "chatbot",
            "mensagem": "Olá! Como posso ajudar?",
            "tipo": "resposta"
        }
    ]
}
```

### GET /chat/receitas

**Response:**
```json
{
    "sucesso": true,
    "receitas": [...],
    "total": 5
}
```

### GET /chat/faqs

**Response:**
```json
{
    "sucesso": true,
    "faqs": [...],
    "total": 8
}
```

## 🎨 Interface do Widget

### Estados

- **Fechado** - Apenas botão ☕ visível
- **Aberto** - Widget completo com histórico
- **Digitando** - Indicador de carregamento
- **Respondendo** - Exibe resposta formatada

### Componentes

```
┌─────────────────────────┐
│ ☕ Maison Café     ✕    │ ← Header
├─────────────────────────┤
│                         │
│ [Mensagens]             │ ← Messages Area
│                         │
├─────────────────────────┤
│ [Input] [Send Button]   │ ← Input Area
└─────────────────────────┘
```

## 🐛 Troubleshooting

### Widget não aparece
- ✅ Verifique se `chatbot_widget.js` está no mesmo diretório
- ✅ Verifique console (F12) para erros
- ✅ Certifique-se que a página está servida por HTTP

### API não responde
- ✅ Verifique se a API está rodando (porta 8000)
- ✅ Veja se há erro de CORS - adicione headers na API
- ✅ Verifique logs do backend

### Respostas genéricas demais
- ✅ Adicione mais FAQs com variações de perguntas
- ✅ Melhore descritores de palavras-chave
- ✅ Implemente busca semântica (opcional)

## 🔐 Segurança

- ✅ Sem dados sensíveis armazenados no cliente
- ✅ Histórico armazenado apenas localmente
- ✅ Validação de entrada no backend
- ✅ CORS configurado (se necessário)

## 📈 Métricas Disponíveis

Via API em `/chat/historico/`:

- Total de mensagens por usuário
- Tipos de perguntas mais frequentes
- Confiança média das respostas
- Taxa de satisfação (pode ser expandida)

## 🚀 Próximas Melhorias

### Em Desenvolvimento
- [ ] Integração com IA real (OpenAI/Gemini)
- [ ] Rating de respostas por usuário
- [ ] Análise de sentimento
- [ ] Suporte a múltiplos idiomas
- [ ] Persistência de histórico no banco
- [ ] Dashboard de análise

## 📞 Suporte

Para dúvidas ou bugs:

1. Verifique a documentação acima
2. Consulte logs da API
3. Verifique console do navegador (F12)
4. Teste com dados simples primeiro

## 📝 Changelog

### v1.0 (Atual)
- ✅ Widget conversacional completo
- ✅ Base de 5 receitas
- ✅ 8 FAQs pré-configuradas
- ✅ Histórico de conversas
- ✅ Sugestões inteligentes
- ✅ Indicador de confiança
- ✅ Interface responsiva
- ✅ Dark mode

---

**Desenvolvido com ❤️ para Maison Café**

*Última atualização: 2026-05-12*
