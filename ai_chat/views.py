from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

def chatbot_page(request):
    """Página HTML do chatbot"""
    return render(request, "ai_chat/chatbot.html")

@csrf_exempt
def chatbot_view(request):
    """Chatbot simples sem OpenAI"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").lower().strip()
            
            # Respostas inteligentes
            if "olá" in user_message or "oi" in user_message or "ola" in user_message:
                resposta = "Olá! Sou o assistente do WS_FTTHEC. Como posso ajudar?"
            elif "inscri" in user_message:
                resposta = "Para se inscrever, vá na página de Inscrição (menu acima) ou acesse /inscricao/"
            elif "ajuda" in user_message:
                resposta = "Posso ajudar com: inscrições, informações do site. Diga 'inscrição' para mais detalhes."
            elif "site" in user_message:
                resposta = "WS_FTTHEC é um sistema ERP com chatbot inteligente."
            elif "funciona" in user_message:
                resposta = "Sim! Estou funcionando perfeitamente agora! 🎉"
            elif "teste" in user_message:
                resposta = "✅ Teste bem-sucedido! O chatbot está respondendo."
            elif "horário" in user_message or "hora" in user_message:
                resposta = "Horário de funcionamento: Segunda a Sexta, 9h às 18h."
            else:
                resposta = f"Entendi: '{user_message}'. Posso ajudar com inscrições ou informações do site WS_FTTHEC."
            
            return JsonResponse({
                "response": resposta,
                "error": False
            })
            
        except Exception as e:
            return JsonResponse({
                "response": f"Erro: {str(e)}",
                "error": True
            })
    
    return JsonResponse({"error": "Método POST necessário"}, status=400)
