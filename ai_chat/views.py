from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ChatHistory, ChatConversion, ChatLead
import uuid

def chatbot_page(request):
    """Página HTML do chatbot"""
    return render(request, "ai_chat/chatbot.html")

@csrf_exempt
def save_chat_lead(request):
    """Salva lead capturado pelo chatbot"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            ChatLead.objects.create(
                session_id=data.get("session_id", ""),
                name=data.get("name", ""),
                email=data.get("email", ""),
                phone=data.get("phone", ""),
                company=data.get("company", ""),
                message=data.get("message", ""),
                source="chatbot"
            )
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"error": "Método POST necessário"}, status=400)

def chat_analytics(request):
    """Página de analytics do chatbot (para admin)"""
    total_conversations = ChatHistory.objects.count()
    total_conversions = ChatConversion.objects.count()
    total_leads = ChatLead.objects.count()

    # Conversões por tipo
    conversions_by_type = {}
    for conv in ChatConversion.objects.all():
        conv_type = conv.conversion_type
        conversions_by_type[conv_type] = conversions_by_type.get(conv_type, 0) + 1

    context = {
        'total_conversations': total_conversations,
        'total_conversions': total_conversions,
        'total_leads': total_leads,
        'conversions_by_type': conversions_by_type,
        'recent_conversations': ChatHistory.objects.all()[:10],
        'recent_conversions': ChatConversion.objects.all()[:10],
        'recent_leads': ChatLead.objects.all()[:10],
    }

    return render(request, "ai_chat/analytics.html", context)

@csrf_exempt
def chatbot_view(request):
    """Chatbot interativo sobre ERP"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").lower().strip()
            session_id = data.get("session_id", str(uuid.uuid4()))

            # Salva histórico do chat
            ChatHistory.objects.create(
                session_id=session_id,
                user_message=user_message,
                bot_response="Processando..."
            )

            # Lógica condicional inteligente:
            if any(word in user_message for word in [
                "o que", "explica", "definição", "significa", "é um erp", "erp é",
                "o que é erp", "explicar erp", "defina erp", "erp significa",
                "como funciona erp", "para que serve erp", "vantagens erp"
            ]):
                # Resposta explicativa sobre o que é ERP
                resposta = """Um ERP (Enterprise Resource Planning) é um sistema integrado de gestão empresarial que unifica todos os processos de uma organização em uma única plataforma.

Principais benefícios:
• Centralização de dados e processos
• Automação de tarefas repetitivas
• Relatórios em tempo real
• Melhoria na tomada de decisões
• Integração entre departamentos (vendas, compras, estoque, financeiro)

O Fthec sistemas e automação é um ERP inteligente com chatbot integrado para transformar seu negócio!"""

            elif any(word in user_message for word in [
                "adquirir", "comprar", "contratar", "contato", "comercial",
                "como conseguir", "quero", "interessado", "demonstração",
                "preço", "custo", "orçamento", "citar", "cotação",
                "implementar", "instalar", "começar", "usar", "teste",
                "avaliação", "proposta", "negócio", "venda", "cliente",
                "empresa", "negociar", "fechar negócio"
            ]):
                # Tracking de conversão
                ChatConversion.objects.create(
                    session_id=session_id,
                    user_message=user_message,
                    conversion_type='demo_request'
                )
                # Resposta direcionando para contato comercial
                resposta = """Excelente! Para adquirir o Fthec sistemas e automação para sua empresa, nossa equipe comercial está pronta para ajudar.

Como prosseguir:
1. 📝 Preencha o formulário de inscrição em nossa página principal
2. 📞 Nossa equipe entrará em contato em até 24h
3. 📊 Receberá uma demonstração personalizada
4. 💰 Orçamento detalhado sem compromisso

<button class="btn btn-primary btn-sm agendar-demo" onclick="window.location.href='/inscricao/'">💬 Fale com especialista</button>

Acesse /inscricao/ ou clique no botão acima para começar!"""

            else:
                # Resposta padrão para outras perguntas
                resposta = """Olá! Sou especialista em ERP. Posso explicar o que é um ERP ou ajudar você a entrar em contato com nossa equipe comercial para adquirir o Fthec sistemas e automação.

Pergunte sobre:
• "O que é um ERP?" - explicação completa
• "Como adquirir um ERP?" - contato comercial"""

            # Atualiza o histórico com a resposta final
            chat_entry = ChatHistory.objects.filter(session_id=session_id).last()
            if chat_entry:
                chat_entry.bot_response = resposta
                chat_entry.save()

            return JsonResponse({
                "response": resposta,
                "session_id": session_id,
                "error": False
            })

        except Exception as e:
            return JsonResponse({
                "response": f"Erro: {str(e)}",
                "error": True
            })

    return JsonResponse({"error": "Método POST necessário"}, status=400)
