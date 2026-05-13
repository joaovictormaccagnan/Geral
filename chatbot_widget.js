/**
 * 🤖 Maison Café Chatbot Widget
 * Widget conversacional interativo para todas as páginas
 */

class ChatbotWidget {
    constructor(config = {}) {
        this.apiBaseUrl = config.apiBaseUrl || 'http://localhost:8000';
        this.usuarioId = config.usuarioId || 'guest';
        this.container = null;
        this.isOpen = false;
        this.historico = [];
        this.init();
    }

    init() {
        // Criar estilos
        this.injetarEstilos();
        // Criar widget
        this.criarWidget();
        // Configurar event listeners
        this.configurarEventos();
    }

    injetarEstilos() {
        const style = document.createElement('style');
        style.innerHTML = `
            /* Chatbot Widget Styles */
            .chatbot-container {
                position: fixed;
                bottom: 20px;
                left: 20px;
                width: 380px;
                height: 600px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 5px 40px rgba(0, 0, 0, 0.16);
                display: none;
                flex-direction: column;
                z-index: 999999;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                overflow: hidden;
                animation: slideUp 0.3s ease-out;
            }

            .chatbot-container.active {
                display: flex;
            }

            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .chatbot-header {
                background: linear-gradient(135deg, #6F4E37 0%, #8B4513 100%);
                color: white;
                padding: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-radius: 12px 12px 0 0;
            }

            .chatbot-header h3 {
                margin: 0;
                font-size: 18px;
                font-weight: 600;
            }

            .chatbot-header p {
                margin: 5px 0 0 0;
                font-size: 12px;
                opacity: 0.9;
            }

            .chatbot-close {
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .chatbot-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
            }

            .message {
                margin-bottom: 15px;
                display: flex;
                animation: fadeIn 0.3s ease-in;
            }

            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .message.user {
                justify-content: flex-end;
            }

            .message.bot {
                justify-content: flex-start;
            }

            .message-content {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 12px;
                word-wrap: break-word;
                line-height: 1.4;
            }

            .user .message-content {
                background: linear-gradient(135deg, #6F4E37 0%, #8B4513 100%);
                color: white;
                border-radius: 18px 18px 4px 18px;
            }

            .bot .message-content {
                background: white;
                color: #333;
                border: 1px solid #e0e0e0;
                border-radius: 18px 18px 18px 4px;
            }

            .message-time {
                font-size: 11px;
                color: #999;
                margin-top: 5px;
                padding: 0 10px;
            }

            .typing-indicator {
                display: flex;
                gap: 4px;
                padding: 12px 16px;
                background: white;
                border-radius: 18px;
                width: fit-content;
                border: 1px solid #e0e0e0;
            }

            .typing-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #999;
                animation: typing 1.4s infinite;
            }

            .typing-dot:nth-child(2) {
                animation-delay: 0.2s;
            }

            .typing-dot:nth-child(3) {
                animation-delay: 0.4s;
            }

            @keyframes typing {
                0%, 60%, 100% {
                    opacity: 0.3;
                    transform: translateY(0);
                }
                30% {
                    opacity: 1;
                    transform: translateY(-10px);
                }
            }

            .chatbot-input-area {
                padding: 15px;
                border-top: 1px solid #e0e0e0;
                display: flex;
                gap: 10px;
                background: white;
            }

            .chatbot-input {
                flex: 1;
                border: 1px solid #ddd;
                border-radius: 24px;
                padding: 12px 16px;
                font-size: 14px;
                outline: none;
                font-family: inherit;
                transition: border-color 0.3s;
            }

            .chatbot-input:focus {
                border-color: #6F4E37;
            }

            .chatbot-send {
                background: linear-gradient(135deg, #6F4E37 0%, #8B4513 100%);
                color: white;
                border: none;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                transition: transform 0.2s;
            }

            .chatbot-send:hover {
                transform: scale(1.05);
            }

            .chatbot-send:active {
                transform: scale(0.95);
            }

            .chatbot-toggle {
                position: fixed;
                bottom: 20px;
                left: 20px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #6F4E37 0%, #8B4513 100%);
                color: white;
                border: none;
                cursor: pointer;
                font-size: 28px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 999998;
                transition: all 0.3s;
            }

            .chatbot-toggle:hover {
                transform: scale(1.1);
            }

            .chatbot-toggle:active {
                transform: scale(0.95);
            }

            .chatbot-toggle.hidden {
                display: none;
            }

            .suggestion-buttons {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 10px;
            }

            .suggestion-btn {
                background: #f0f0f0;
                border: 1px solid #ddd;
                padding: 8px 12px;
                border-radius: 16px;
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s;
                max-width: 100%;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .suggestion-btn:hover {
                background: #e0e0e0;
                border-color: #6F4E37;
            }

            /* Responsivo */
            @media (max-width: 480px) {
                .chatbot-container {
                    width: 100%;
                    height: 100%;
                    bottom: 0;
                    right: 0;
                    border-radius: 0;
                }
            }

            /* Dark mode */
            @media (prefers-color-scheme: dark) {
                .chatbot-container {
                    background: #1e1e1e;
                }

                .chatbot-messages {
                    background: #2a2a2a;
                }

                .bot .message-content {
                    background: #333;
                    color: #f0f0f0;
                    border-color: #444;
                }

                .chatbot-input {
                    background: #333;
                    color: #f0f0f0;
                    border-color: #444;
                }

                .suggestion-btn {
                    background: #333;
                    border-color: #444;
                    color: #f0f0f0;
                }

                .suggestion-btn:hover {
                    background: #444;
                    border-color: #6F4E37;
                }
            }
        `;
        document.head.appendChild(style);
    }

    criarWidget() {
        // Botão toggle
        this.botaoToggle = document.createElement('button');
        this.botaoToggle.className = 'chatbot-toggle';
        this.botaoToggle.innerHTML = '☕';
        this.botaoToggle.title = 'Abrir Chatbot';
        document.body.appendChild(this.botaoToggle);

        // Container do chatbot
        this.container = document.createElement('div');
        this.container.className = 'chatbot-container';
        this.container.innerHTML = `
            <div class="chatbot-header">
                <div>
                    <h3>☕ Maison Café</h3>
                    <p>Como posso ajudar?</p>
                </div>
                <button class="chatbot-close">✕</button>
            </div>
            <div class="chatbot-messages" id="chatbot-messages"></div>
            <div class="chatbot-input-area">
                <input 
                    type="text" 
                    class="chatbot-input" 
                    placeholder="Faça uma pergunta..." 
                    id="chatbot-input"
                />
                <button class="chatbot-send" id="chatbot-send">➤</button>
            </div>
        `;
        document.body.appendChild(this.container);

        // Referências rápidas
        this.messagesDiv = this.container.querySelector('#chatbot-messages');
        this.inputField = this.container.querySelector('#chatbot-input');
        this.sendButton = this.container.querySelector('#chatbot-send');
        this.closeButton = this.container.querySelector('.chatbot-close');

        // Mensagem inicial
        this.exibirMensagem('bot', '👋 Olá! Bem-vindo ao Maison Café!\n\nSou um assistente IA. Posso ajudar com:\n\n📖 Receitas\n❓ Dúvidas sobre o site\n☕ Cardápio\n🛒 Pedidos\n\nO que você gostaria de saber?');
    }

    configurarEventos() {
        // Toggle do chatbot
        this.botaoToggle.addEventListener('click', () => this.toggleChat());
        this.closeButton.addEventListener('click', () => this.toggleChat());

        // Enviar mensagem
        this.sendButton.addEventListener('click', () => this.enviarMensagem());
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.enviarMensagem();
        });

        // Focar no input ao abrir
        this.container.addEventListener('class', () => {
            if (this.container.classList.contains('active')) {
                this.inputField.focus();
            }
        });
    }

    toggleChat() {
        this.container.classList.toggle('active');
        this.botaoToggle.classList.toggle('hidden');
        if (this.container.classList.contains('active')) {
            this.inputField.focus();
        }
    }

    enviarMensagem() {
        const mensagem = this.inputField.value.trim();
        if (!mensagem) return;

        // Limpar input
        this.inputField.value = '';

        // Exibir mensagem do usuário
        this.exibirMensagem('user', mensagem);

        // Mostrar indicador de digitação
        this.exibirIndicadorDigitacao();

        // Enviar para o backend
        this.enviarParaBotIA(mensagem);
    }

    exibirMensagem(tipo, conteudo, confianca = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${tipo}`;

        // Substituir quebras de linha por <br>
        const conteudoFormatado = conteudo.replace(/\n/g, '<br>');

        let html = `
            <div class="message-content">
                ${conteudoFormatado}
        `;

        // Adicionar confiança se for resposta bot
        if (tipo === 'bot' && confianca) {
            html += `<div style="font-size: 11px; margin-top: 5px; opacity: 0.7;">Confiança: ${confianca}%</div>`;
        }

        html += '</div>';

        // Adicionar hora
        const agora = new Date();
        const hora = agora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
        html += `<div class="message-time">${hora}</div>`;

        messageDiv.innerHTML = html;
        this.messagesDiv.appendChild(messageDiv);

        // Scroll para baixo
        this.messagesDiv.scrollTop = this.messagesDiv.scrollHeight;

        // Armazenar no histórico
        this.historico.push({ tipo, conteudo, hora });
    }

    exibirIndicadorDigitacao() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        messageDiv.id = 'typing-indicator';
        messageDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        this.messagesDiv.appendChild(messageDiv);
        this.messagesDiv.scrollTop = this.messagesDiv.scrollHeight;
    }

    removerIndicadorDigitacao() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }

    enviarParaBotIA(mensagem) {
        const url = `${this.apiBaseUrl}/chat`;
        const payload = {
            mensagem: mensagem,
            usuario_id: this.usuarioId
        };

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            this.removerIndicadorDigitacao();

            if (data.sucesso) {
                // Exibir resposta
                this.exibirMensagem('bot', data.resposta, data.confianca);

                // Exibir sugestões
                if (data.sugestoes && data.sugestoes.length > 0) {
                    this.exibirSugestoes(data.sugestoes);
                }
            } else {
                this.exibirMensagem('bot', '❌ Desculpe, ocorreu um erro. Tente novamente.');
            }
        })
        .catch(error => {
            this.removerIndicadorDigitacao();
            console.error('Erro ao conectar com chatbot:', error);
            this.exibirMensagem('bot', '⚠️ Erro de conexão. Verifique se a API está ativa.');
        });
    }

    exibirSugestoes(sugestoes) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';

        let html = '<div class="suggestion-buttons">';
        sugestoes.forEach(sugestao => {
            html += `<button class="suggestion-btn">${sugestao}</button>`;
        });
        html += '</div>';

        messageDiv.innerHTML = html;
        this.messagesDiv.appendChild(messageDiv);

        // Adicionar event listeners aos botões
        messageDiv.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.inputField.value = btn.textContent;
                this.enviarMensagem();
            });
        });

        this.messagesDiv.scrollTop = this.messagesDiv.scrollHeight;
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new ChatbotWidget({
        apiBaseUrl: 'http://127.0.0.1:8000'
    });
});
