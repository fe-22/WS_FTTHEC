# ai_chat/views.py atualizado
import json
import os
import uuid
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import ChatHistory

# Initialize OpenAI if API key is available
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY

@csrf_exempt
def chat_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            # Get or create session ID
            session_id = request.session.get('chat_session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
                request.session['chat_session_id'] = session_id
            
            # Save user message to database
            chat_history = ChatHistory.objects.create(
                session_id=session_id,
                user_message=user_message,
                bot_response=""
            )
            
            # Check if OpenAI is configured
            if settings.OPENAI_API_KEY:
                try:
                    # Use OpenAI API
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": """Você é um assistente virtual especializado em sistemas ERP para varejo da empresa ERP Solutions. 
                                Você deve ser prestativo, profissional e focado em resolver problemas de gestão empresarial.
                                
                                Produtos da empresa:
                                1. ERP Completo - Sistema integrado de gestão empresarial
                                2. ModerLoja - Sistema específico para varejo com PDV e e-commerce
                                
                                Sempre que possível, sugira agendar uma demonstração gratuita.
                                Seja claro e direto nas respostas."""
                            },
                            {
                                "role": "user",
                                "content": user_message
                            }
                        ],
                        max_tokens=200,
                        temperature=0.7
                    )
                    
                    bot_response = response.choices[0].message.content
                    
                except Exception as e:
                    print(f"OpenAI error: {e}")
                    # Fallback to predefined responses if OpenAI fails
                    bot_response = get_predefined_response(user_message)
            else:
                # Use predefined responses if no OpenAI key
                bot_response = get_predefined_response(user_message)
            
            # Update chat history with bot response
            chat_history.bot_response = bot_response
            chat_history.save()
            
            return JsonResponse({'response': bot_response})
            
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'response': 'Desculpe, ocorreu um erro. Por favor, entre em contato pelo telefone (11) 99999-9999.'})
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)

def get_predefined_response(message):
    """Fallback responses when OpenAI is not available"""
    message_lower = message.lower()
    
    # Define keyword mappings
    responses = {
        'saudacao': ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite', 'hello', 'hi'],
        'erp': ['erp', 'sistema', 'software', 'gestão', 'gerenciamento'],
        'moderloja': ['moderloja', 'moder loja', 'loja', 'varejo', 'pdv'],
        'preco': ['preço', 'valor', 'custo', 'quanto custa', 'quanto é', 'precos'],
        'demonstracao': ['demonstração', 'teste', 'experimentar', 'agendar', 'marcar'],
        'estoque': ['estoque', 'inventário', 'produtos', 'mercadoria'],
        'pdv': ['pdv', 'caixa', 'vendas', 'ponto de venda', 'registradora'],
        'financeiro': ['financeiro', 'contas', 'fluxo', 'dinheiro', 'pagamentos'],
        'suporte': ['suporte', 'ajuda', 'problema', 'erro', 'dúvida'],
        'integracao': ['integração', 'conectar', 'api', 'loja virtual', 'marketplace'],
        'relatorios': ['relatórios', 'relatorio', 'dados', 'dashboard', 'gráficos']
    }
    
    # Check for matches
    for category, keywords in responses.items():
        if any(keyword in message_lower for keyword in keywords):
            return get_response_by_category(category, message)
    
    # Default response
    return get_response_by_category('default', message)

def get_response_by_category(category, original_message):
    """Return specific response based on category"""
    responses = {
        'saudacao': 'Olá! Sou o assistente da ERP Solutions. Posso ajudar com informações sobre nossos sistemas ERP e ModerLoja. Como posso ajudar sua empresa hoje?',
        'erp': 'Nosso ERP completo oferece módulos integrados: • Controle de estoque • Vendas/PDV • Financeiro • Clientes • Relatórios • Fiscal. Qual área da sua empresa você gostaria de otimizar?',
        'moderloja': 'O ModerLoja é perfeito para varejo! Oferece: • PDV completo • Loja virtual • Integração com marketplaces • Controle de estoque • Relatórios inteligentes. Ideal para quem quer vender online e offline!',
        'preco': 'Temos planos flexíveis que se adaptam ao seu negócio. Para uma cotação personalizada, recomendo agendar uma demonstração gratuita com nosso time comercial.',
        'demonstracao': 'Ótimo! Para agendar uma demonstração gratuita: 1) Clique em "Demonstração Gratuita" no site 2) Preencha o formulário 3) Entraremos em contato em até 24h. Posso ajudar com mais alguma coisa?',
        'estoque': 'Módulo de Estoque: • Controle em tempo real • Alertas automáticos de reposição • Inventário periódico • Custo médio e FIFO • Integração total com vendas e compras.',
        'pdv': 'PDV Completo: • Vendas rápidas com busca por código/descrição • Múltiplas formas de pagamento • NFC-e instantânea • Controle de comissões • Fechamento de caixa automatizado.',
        'financeiro': 'Módulo Financeiro: • Contas a pagar/receber • Fluxo de caixa projetado • Conciliação bancária • Relatórios gerenciais • Previsões financeiras.',
        'suporte': 'Nosso suporte é especializado! Oferecemos: • Atendimento por telefone/WhatsApp • Suporte remoto • Treinamentos • Atualizações gratuitas. Para suporte urgente: (11) 99999-9999.',
        'integracao': 'Integramos com: • Loja Virtual WooCommerce • Marketplaces (Mercado Livre, Shopee) • Bancos • Correios • Sistemas contábeis. Sua operação totalmente conectada!',
        'relatorios': 'Relatórios Inteligentes: • Dashboard executivo • Análise de vendas • Rentabilidade por produto • Performance de vendedores • Gráficos interativos.',
        'default': f'Entendi que você perguntou sobre "{original_message}". Para uma resposta mais específica, recomendo: 1) Agendar uma demonstração gratuita 2) Falar com nosso time pelo WhatsApp (11) 99999-9999 3) Explorar nosso site para mais detalhes!'
    }
    
    return responses.get(category, responses['default'])