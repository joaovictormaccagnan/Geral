"""
🤖 CHATBOT IA - Maison Café com Ollama
Responde perguntas sobre receitas, produtos e suporte ao site
Usa Ollama (IA local) com fallback para base de conhecimento local
"""

import json
import os
import urllib.request
import urllib.error
from typing import Dict, List

# ============================================================
# CONFIGURAÇÃO OLLAMA
# ============================================================
# Endereço padrão do Ollama (rodando localmente)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Modelo a usar - altere para o modelo que você tiver instalado
# Exemplos: "llama3", "llama3.2", "mistral", "gemma2", "phi3"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")  # Altere para o modelo que você tem

# BASE DE CONHECIMENTO - FAQs e Receitas
KNOWLEDGE_BASE = {
    "receitas": [
        {
            "nome": "Café Expresso",
            "ingredientes": ["30ml café coado", "5ml xarope de baunilha", "Espuma de leite"],
            "preparo": "Coar o café, adicionar xarope e cobertura de espuma",
            "tempo": "5 minutos",
            "dificuldade": "Fácil"
        },
        {
            "nome": "Cappuccino",
            "ingredientes": ["30ml café expresso", "20ml leite vaporizado", "30ml espuma"],
            "preparo": "Preparar espresso, vaporizar leite e cobrir com espuma abundante",
            "tempo": "8 minutos",
            "dificuldade": "Fácil"
        },
        {
            "nome": "Café com Leite",
            "ingredientes": ["60ml café coado", "120ml leite quente", "Açúcar opcional"],
            "preparo": "Misturar café com leite quente. Adicionar açúcar a gosto",
            "tempo": "10 minutos",
            "dificuldade": "Muito Fácil"
        },
        {
            "nome": "Mocha",
            "ingredientes": ["30ml café expresso", "20ml chocolate derretido", "80ml leite", "Açúcar"],
            "preparo": "Misturar chocolate com café, adicionar leite e cobrir com espuma",
            "tempo": "12 minutos",
            "dificuldade": "Média"
        },
        {
            "nome": "Café Gelado",
            "ingredientes": ["120ml café frio", "Gelo", "60ml leite", "Açúcar"],
            "preparo": "Coar café e deixar esfriar. Servir com gelo e leite",
            "tempo": "5 minutos (+ repouso)",
            "dificuldade": "Fácil"
        }
    ],
    "faqs": [
        {
            "pergunta": "Como faço um pedido?",
            "resposta": "Acesse nosso site, browse o cardápio, adicione itens ao carrinho e siga o processo de checkout. Você pode pagar online ou na entrega."
        },
        {
            "pergunta": "Qual é o tempo de entrega?",
            "resposta": "Entregamos em até 30 minutos dentro da região coberta. Consulte o endereço de entrega ao finalizar o pedido."
        },
        {
            "pergunta": "Vocês entregam à noite?",
            "resposta": "Sim! Operamos de segunda a domingo de 6:00 às 23:00. Pedidos noturnos também são bem-vindos."
        },
        {
            "pergunta": "Como rastrear meu pedido?",
            "resposta": "Após confirmar o pedido, você receberá um código de rastreamento por email. Pode consultá-lo na seção 'Meus Pedidos'."
        },
        {
            "pergunta": "Qual é a forma de pagamento?",
            "resposta": "Aceitamos cartão de crédito, débito, PIX e dinheiro na entrega. Escolha a opção durante o checkout."
        },
        {
            "pergunta": "Posso cancelar um pedido?",
            "resposta": "Sim, você pode cancelar nos primeiros 10 minutos após a confirmação. Acesse 'Meus Pedidos' e selecione cancelar."
        },
        {
            "pergunta": "Vocês oferecem café descafeinado?",
            "resposta": "Sim! Todos os nossos drinks podem ser preparados com café descafeinado. Especifique na hora do pedido."
        },
        {
            "pergunta": "Há opções veganas?",
            "resposta": "Absolutamente! Oferecemos leite de aveia, amêndoa e soja. Peça para substituir o leite em qualquer bebida."
        }
    ],
    "categorias": [
        "bebidas", "alimentos", "receitas", "pedidos", "entrega", "pagamento",
        "cardápio", "cupons", "suporte", "sobre"
    ]
}


class ChatbotIA:
    """Chatbot inteligente com Ollama (IA local) + fallback local"""

    def __init__(self):
        self.historico = []
        self.usando_ollama = False
        self.modo_atual = "local"

        # Verificar se Ollama está disponível
        self._verificar_ollama()

    def _verificar_ollama(self):
        """Verifica se Ollama está rodando e o modelo está disponível"""
        try:
            req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                modelos = [m["name"].split(":")[0] for m in data.get("models", [])]

                if OLLAMA_MODEL.split(":")[0] in modelos or any(OLLAMA_MODEL in m for m in modelos):
                    self.usando_ollama = True
                    self.modo_atual = f"Ollama ({OLLAMA_MODEL})"
                    print(f"✅ Ollama conectado! Modelo: {OLLAMA_MODEL}")
                else:
                    modelos_str = ", ".join(modelos) if modelos else "nenhum"
                    print(f"⚠️ Modelo '{OLLAMA_MODEL}' não encontrado no Ollama.")
                    print(f"   Modelos disponíveis: {modelos_str}")
                    print(f"   Para instalar: ollama pull {OLLAMA_MODEL}")
                    print("   Usando IA local como fallback.")
                    self.modo_atual = "local"

        except Exception as e:
            print(f"⚠️ Ollama não encontrado em {OLLAMA_URL}: {e}")
            print("   Certifique-se que o Ollama está rodando: ollama serve")
            print("   Usando IA local como fallback.")
            self.modo_atual = "local"

    def processar_entrada(self, mensagem: str, usuario_id: str = "guest") -> Dict:
        """Processa a entrada do usuário com Ollama (se disponível) ou fallback local"""
        mensagem = mensagem.strip()

        # Armazenar no histórico
        self.historico.append({
            "usuario": usuario_id,
            "mensagem": mensagem,
            "tipo": "pergunta"
        })

        # Tentar Ollama primeiro
        if self.usando_ollama:
            resposta_texto = self._gerar_resposta_ollama(mensagem)
        else:
            resposta_texto = self._gerar_resposta_local(mensagem)

        # Armazenar resposta
        self.historico.append({
            "usuario": "chatbot",
            "mensagem": resposta_texto,
            "tipo": "resposta"
        })

        return {
            "resposta": resposta_texto,
            "confianca": 95 if self.usando_ollama else 75,
            "sugestoes": self._gerar_sugestoes(mensagem),
            "tipo": "resposta_normal",
            "modo": self.modo_atual
        }

    def _gerar_resposta_ollama(self, mensagem: str) -> str:
        """Usa Ollama para gerar resposta inteligente"""
        try:
            system_prompt = """Você é um assistente virtual do Maison Café, uma cafeteria especializada.

Informações do Maison Café:
- Funcionamento: segunda a domingo, 6:00 às 23:00
- Entrega: até 30 minutos dentro da região coberta
- Pagamento: cartão de crédito, débito, PIX e dinheiro na entrega
- Especialidade: cafés, doces franceses, lanches
- Opções: café descafeinado disponível; leite de aveia/amêndoa/soja para veganos
- Cancelamento: pode cancelar pedido nos primeiros 10 minutos

Receitas disponíveis: Café Expresso, Cappuccino, Café com Leite, Mocha, Café Gelado.

Responda SEMPRE em português brasileiro, de forma amigável, concisa e útil.
Se não souber algo específico, seja honesto e sugira contato com o Maison Café.
Não invente preços ou informações que não foram fornecidas."""

            payload = json.dumps({
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": mensagem}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 300
                }
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{OLLAMA_URL}/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                resposta = data.get("message", {}).get("content", "").strip()

                if resposta:
                    print(f"✅ Resposta via Ollama ({OLLAMA_MODEL})")
                    return resposta
                else:
                    print("⚠️ Ollama retornou resposta vazia, usando fallback")
                    return self._gerar_resposta_local(mensagem)

        except urllib.error.URLError as e:
            print(f"⚠️ Ollama offline ou inacessível: {e}")
            print("🔄 Ativando fallback para IA local...")
            self.usando_ollama = False
            self.modo_atual = "local (Ollama offline)"
            return self._gerar_resposta_local(mensagem)

        except Exception as e:
            print(f"⚠️ Erro ao chamar Ollama: {e}")
            return self._gerar_resposta_local(mensagem)

    def _gerar_resposta_local(self, mensagem: str) -> str:
        """Gera resposta usando base de conhecimento local (fallback)"""
        msg = mensagem.lower()

        # Saudações
        if any(s in msg for s in ["oi", "olá", "ola", "opa", "e aí", "eai", "bom dia", "boa tarde", "boa noite"]):
            return "👋 Olá! Bem-vindo ao Maison Café! Como posso ajudar? Posso responder dúvidas sobre nossos produtos, receitas, pedidos ou entrega."

        # Despedidas
        if any(s in msg for s in ["tchau", "até", "falou", "adeus", "bye", "obrigado", "valeu"]):
            return "👋 Até logo! Obrigado por usar o Maison Café. Volte sempre! ☕"

        # Receitas
        if any(p in msg for p in ["receita", "como fazer", "preparar", "ingredientes", "modo de preparo"]):
            return self._responder_receitas(msg)

        # FAQs
        faq_resposta = self._buscar_faq(msg)
        if faq_resposta:
            return faq_resposta

        # Cardápio e produtos
        if any(p in msg for p in ["cardápio", "cardapio", "menu", "produtos", "bebidas", "alimentos", "o que vocês vendem", "o que tem"]):
            return "☕ Nosso cardápio inclui: Cafés especiais, Cappuccino, Mocha, Café com Leite, Bebidas Geladas e muito mais! Visite nosso site para ver os preços e fazer seu pedido."

        # Pedidos
        if any(p in msg for p in ["pedido", "comprar", "fazer pedido", "encomendar"]):
            return "🛒 Para fazer um pedido, acesse nosso site, selecione os itens desejados e siga o processo de checkout. Oferecemos várias formas de pagamento. Precisa de ajuda com algo específico?"

        # Entrega
        if any(p in msg for p in ["entrega", "prazo", "quanto tempo", "quando chega", "taxa"]):
            return "🚚 Entregamos em até 30 minutos dentro da região coberta. A taxa de entrega varia conforme a localização. Consulte ao finalizar o pedido."

        # Pagamento
        if any(p in msg for p in ["pagamento", "cartão", "cartao", "pix", "boleto", "dinheiro", "pagar"]):
            return "💳 Aceitamos: Cartão de Crédito, Débito, PIX e Dinheiro na Entrega. Escolha sua opção preferida durante o checkout."

        # Horário
        if any(p in msg for p in ["horário", "horario", "abre", "fecha", "funcionamento", "aberto"]):
            return "⏰ Funcionamos de segunda a domingo de 6:00 às 23:00. Estamos sempre prontos para atender você! ☕"

        # Sobre nós
        if any(p in msg for p in ["quem são", "sobre", "história", "historia", "maison café", "maison cafe"]):
            return "🏢 Somos o Maison Café, sua cafeteria especializada em bebidas de qualidade! Atendemos com os melhores cafés e excelente atendimento. Visite-nos!"

        # Contato
        if any(p in msg for p in ["contato", "telefone", "whatsapp", "email", "endereço", "endereco"]):
            return "📞 Entre em contato conosco:\n📱 WhatsApp: (11) 9XXXX-XXXX\n📧 Email: contato@maisoncafe.com\n📍 Rua Principal, 123"

        # Fallback
        return ("🤔 Não entendi muito bem. Posso ajudar com:\n"
                "- 📖 Receitas de café\n"
                "- ❓ Dúvidas sobre pedidos e entrega\n"
                "- ☕ Cardápio\n"
                "- 💳 Formas de pagamento\n"
                "- 📞 Contato\n\n"
                "Qual desses tópicos te interessa?")

    def _responder_receitas(self, mensagem: str) -> str:
        """Busca e retorna receitas"""
        receitas_filtradas = []

        for receita in KNOWLEDGE_BASE["receitas"]:
            nome_lower = receita["nome"].lower()
            if any(p in mensagem for p in [nome_lower, nome_lower.split()[0]]):
                receitas_filtradas.append(receita)

        if not receitas_filtradas:
            nomes = ", ".join([r["nome"] for r in KNOWLEDGE_BASE["receitas"]])
            return f"📖 Temos receitas de: {nomes}\n\nQual você gostaria de preparar?"

        resposta = ""
        for receita in receitas_filtradas:
            resposta += f"""
🍵 **{receita['nome']}**
⏱️ Tempo: {receita['tempo']}
📊 Dificuldade: {receita['dificuldade']}

📋 **Ingredientes:**
{chr(10).join(['• ' + ing for ing in receita['ingredientes']])}

👨‍🍳 **Modo de Preparo:**
{receita['preparo']}
"""
        return resposta.strip()

    def _buscar_faq(self, mensagem: str) -> str:
        """Busca resposta em FAQs por similaridade Jaccard"""
        melhor_match = None
        melhor_score = 0

        for faq in KNOWLEDGE_BASE["faqs"]:
            score = self._calcular_similaridade(mensagem, faq["pergunta"].lower())
            if score > melhor_score:
                melhor_score = score
                melhor_match = faq

        if melhor_score > 0.3:
            return melhor_match["resposta"]
        return None

    def _calcular_similaridade(self, texto1: str, texto2: str) -> float:
        """Similaridade de Jaccard entre dois textos"""
        palavras1 = set(texto1.split())
        palavras2 = set(texto2.split())
        if not palavras1 or not palavras2:
            return 0
        intersecao = len(palavras1 & palavras2)
        uniao = len(palavras1 | palavras2)
        return intersecao / uniao if uniao > 0 else 0

    def _gerar_sugestoes(self, mensagem: str) -> List[str]:
        """Gera sugestões de próximas perguntas"""
        sugestoes = [
            "Ver receitas",
            "Como fazer um pedido?",
            "Qual o horário de funcionamento?",
            "Formas de pagamento"
        ]
        if "receita" in mensagem:
            sugestoes = ["Outra receita", "Como fazer pedido?", "Contato"]
        elif "pedido" in mensagem:
            sugestoes = ["Tempo de entrega", "Formas de pagamento", "Ver receitas"]
        elif "entrega" in mensagem:
            sugestoes = ["Taxa de entrega", "Horário de funcionamento", "Fazer pedido"]
        return sugestoes

    def obter_historico(self, usuario_id: str = None) -> List:
        """Retorna histórico de conversa"""
        if usuario_id:
            return [m for m in self.historico if m.get("usuario") == usuario_id or m.get("usuario") == "chatbot"]
        return self.historico


# Instância global
chatbot = ChatbotIA()
