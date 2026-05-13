"""
🤖 CHATBOT IA - Maison Café com Google Gemini
Responde perguntas sobre receitas, produtos e suporte ao site
Usa Gemini IA com fallback para base de conhecimento local
"""

import json
import re
import os
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar Google Gemini
try:
    import google.generativeai as genai
    GEMINI_DISPONIVEL = True
except ImportError:
    GEMINI_DISPONIVEL = False
    print("⚠️ Google Generative AI não instalado. Usando fallback local.")

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
    """Chatbot inteligente com Google Gemini + fallback local"""
    
    def __init__(self):
        self.historico = []
        self.usuarios_ativos = {}
        self.usando_gemini = False
        self.modo_atual = "local"
        
        # Configurar Gemini
        if GEMINI_DISPONIVEL:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key and api_key != "seu_api_key_aqui":
                try:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-pro')
                    self.usando_gemini = True
                    self.modo_atual = "Gemini IA"
                    print("✅ Google Gemini IA configurado com sucesso!")
                except Exception as e:
                    print(f"⚠️ Erro ao configurar Gemini: {e}")
                    self.usando_gemini = False
                    self.modo_atual = "local"
            else:
                print("⚠️ GEMINI_API_KEY não configurada. Usando IA local.")
                self.modo_atual = "local"
        else:
            print("⚠️ Google Generative AI não disponível. Usando IA local.")
            self.modo_atual = "local"
        
    def processar_entrada(self, mensagem: str, usuario_id: str = "guest") -> Dict:
        """
        Processa a entrada do usuário com Gemini (se disponível) ou fallback local
        """
        mensagem = mensagem.strip()
        
        # Armazenar no histórico
        self.historico.append({
            "usuario": usuario_id,
            "mensagem": mensagem,
            "tipo": "pergunta"
        })
        
        # Tentar Gemini primeiro
        if self.usando_gemini:
            resposta = self._gerar_resposta_gemini(mensagem, usuario_id)
        else:
            # Fallback: usar base de conhecimento local
            resposta = self._gerar_resposta_local(mensagem)
        
        # Armazenar resposta
        self.historico.append({
            "usuario": "chatbot",
            "mensagem": resposta,
            "tipo": "resposta"
        })
        
        return {
            "resposta": resposta,
            "confianca": 95 if self.usando_gemini else 75,
            "sugestoes": self._gerar_sugestoes(mensagem),
            "tipo": "resposta_normal",
            "modo": self.modo_atual
        }
    
    def _gerar_resposta_gemini(self, mensagem: str, usuario_id: str) -> str:
        """
        Usa Google Gemini IA para gerar resposta inteligente
        Com fallback automático se falhar
        """
        try:
            # Contexto do Maison Café
            contexto = """Você é um assistente de IA para o Maison Café, uma cafeteria especializada.
            
Informações do Maison Café:
- Funcionamento: segunda a domingo, 6:00 às 23:00
- Entrega: até 30 minutos dentro da região coberta
- Aceita: cartão crédito, débito, PIX e dinheiro na entrega
- Especialidade: cafés, doces franceses, lanches
- Oferece: café descafeinado, leite de aveia/amêndoa/soja para veganos

Responda sempre em português, de forma amigável e útil.
Se não souber algo específico, seja honesto e sugira contato com o Maison Café."""

            prompt = f"{contexto}\n\nCliente pergunta: {mensagem}\n\nResponda de forma concisa e amigável:"
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                print(f"✅ Resposta via Gemini IA")
                return response.text
            else:
                # Falha na resposta, usar fallback
                print("⚠️ Gemini retornou resposta vazia, usando fallback")
                self.usando_gemini = False
                self.modo_atual = "local"
                return self._gerar_resposta_local(mensagem)
                
        except Exception as e:
            print(f"⚠️ Erro Gemini: {e}")
            print("🔄 Ativando fallback para IA local...")
            
            # Se limite de API atingido, desabilitar Gemini
            if "429" in str(e) or "quota" in str(e).lower():
                print("⚠️ Limite da API atingida! Usando IA local de agora em diante.")
                self.usando_gemini = False
                self.modo_atual = "local (limite Gemini excedido)"
            
            # Usar fallback local
            return self._gerar_resposta_local(mensagem)
    
    def _gerar_resposta_local(self, mensagem: str) -> str:
        """
        Gera resposta usando base de conhecimento local
        (Usado como fallback quando Gemini não está disponível)
        """
        
        # Saudações
        if any(saudacao in mensagem for saudacao in ["oi", "olá", "opa", "e aí", "opa"]):
            return "👋 Olá! Bem-vindo ao Maison Café! Como posso ajudar? Posso responder dúvidas sobre nossos produtos, receitas, pedidos ou entrega."
        
        # Despedidas
        if any(desp in mensagem for desp in ["tchau", "até", "falou", "adeus", "bye"]):
            return "👋 Até logo! Obrigado por usar o Maison Café. Volte sempre! ☕"
        
        # Receitas
        if any(palavra in mensagem for palavra in ["receita", "como fazer", "preparar", "ingredientes", "modo de preparo"]):
            return self._responder_receitas(mensagem)
        
        # FAQs
        faq_resposta = self._buscar_faq(mensagem)
        if faq_resposta:
            return faq_resposta
        
        # Cardápio e produtos
        if any(palavra in mensagem for palavra in ["cardápio", "menu", "produtos", "bebidas", "alimentos", "o que vocês vendem"]):
            return "☕ Nosso cardápio inclui: Cafés especiais, Cappuccino, Mocha, Café com Leite, Bebidas Geladas e muito mais! Visite nosso site para ver os preços e fazer seu pedido."
        
        # Pedidos
        if any(palavra in mensagem for palavra in ["pedido", "comprar", "fazer pedido", "encomendar"]):
            return "🛒 Para fazer um pedido, acesse nosso site, selecione os itens desejados e siga o processo de checkout. Oferecemos várias formas de pagamento. Precisa de ajuda com algo específico?"
        
        # Entrega
        if any(palavra in mensagem for palavra in ["entrega", "prazo", "quanto tempo", "quando chega", "taxa"]):
            return "🚚 Entregamos em até 30 minutos dentro da região coberta. A taxa de entrega varia conforme a localização. Consulte ao finalizar o pedido para ver a taxa e tempo exato."
        
        # Pagamento
        if any(palavra in mensagem for palavra in ["pagamento", "forma de pagamento", "cartão", "pix", "boleto", "dinheiro"]):
            return "💳 Aceitamos: Cartão de Crédito, Débito, PIX e Dinheiro na Entrega. Escolha sua opção preferida durante o checkout."
        
        # Horário
        if any(palavra in mensagem for palavra in ["horário", "abre", "fecha", "funcionamento", "aberto"]):
            return "⏰ Funcionamos de segunda a domingo de 6:00 às 23:00. Estamos sempre prontos para atender você! ☕"
        
        # Sobre nós
        if any(palavra in mensagem for palavra in ["quem são", "sobre", "história", "maison café"]):
            return "🏢 Somos o Maison Café, sua café especializado em bebidas de qualidade! Desde 2020 servindo os melhores cafés com excelente atendimento. Visite-nos!"
        
        # Contato
        if any(palavra in mensagem for palavra in ["contato", "telefone", "whatsapp", "email", "endereço"]):
            return "📞 Entre em contato conosco:\n📱 WhatsApp: (11) 9XXXX-XXXX\n📧 Email: contato@maisonca fé.com\n📍 Rua Principal, 123"
        
        # Fallback
        return "🤔 Hmm, não entendi muito bem sua pergunta. Posso ajudar com:\n- 📖 Receitas\n- ❓ FAQs sobre pedidos e entrega\n- ☕ Cardápio\n- 🛒 Como fazer pedidos\n- 📞 Informações de contato\n\nQual desses tópicos te interessa?"
    
    def _responder_receitas(self, mensagem: str) -> str:
        """Busca e retorna receitas"""
        
        receitas_filtradas = []
        
        for receita in KNOWLEDGE_BASE["receitas"]:
            if any(palavra in mensagem for palavra in [receita["nome"].lower(), receita["nome"].lower().split()[0]]):
                receitas_filtradas.append(receita)
        
        if not receitas_filtradas:
            # Se não encontrou específica, lista todas
            receitas_nomes = ", ".join([r["nome"] for r in KNOWLEDGE_BASE["receitas"]])
            return f"📖 Temos receitas de: {receitas_nomes}\n\nQual você gostaria de preparar?"
        
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
        """Busca resposta em FAQs"""
        
        melhor_match = None
        melhor_score = 0
        
        for faq in KNOWLEDGE_BASE["faqs"]:
            pergunta_lower = faq["pergunta"].lower()
            score = self._calcular_similaridade(mensagem, pergunta_lower)
            
            if score > melhor_score:
                melhor_score = score
                melhor_match = faq
        
        if melhor_score > 0.3:  # Threshold mínimo
            return melhor_match["resposta"]
        
        return None
    
    def _calcular_similaridade(self, texto1: str, texto2: str) -> float:
        """Calcula similaridade entre dois textos (Jaccard)"""
        
        palavras1 = set(texto1.split())
        palavras2 = set(texto2.split())
        
        if not palavras1 or not palavras2:
            return 0
        
        intersecao = len(palavras1 & palavras2)
        uniao = len(palavras1 | palavras2)
        
        return intersecao / uniao if uniao > 0 else 0
    
    def _calcular_confianca(self, entrada: str, resposta: str) -> float:
        """Calcula confiança da resposta (0-100%)"""
        
        # Se é resposta de FAQ com alta similaridade
        melhor_score = 0
        for faq in KNOWLEDGE_BASE["faqs"]:
            score = self._calcular_similaridade(entrada, faq["pergunta"].lower())
            melhor_score = max(melhor_score, score)
        
        # Converter para porcentagem
        confianca = min(int(melhor_score * 100), 100)
        return max(confianca, 50)  # Mínimo 50%
    
    def _gerar_sugestoes(self, mensagem: str) -> List[str]:
        """Gera sugestões de próximas perguntas"""
        
        sugestoes = [
            "Ver receitas",
            "Como fazer um pedido?",
            "Qual o horário de funcionamento?",
            "Formas de pagamento"
        ]
        
        # Adaptar sugestões baseado na entrada
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
            return [msg for msg in self.historico if msg.get("usuario") == usuario_id or msg.get("usuario") == "chatbot"]
        return self.historico

# Instância global
chatbot = ChatbotIA()
