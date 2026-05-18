import json
import os
import uuid

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import ChatConversion, ChatHistory, ChatLead

try:
    from google.cloud import firestore
except ImportError:
    firestore = None


def _get_firestore_client():
    if firestore is None:
        return None
    try:
        project_id = os.getenv("FIRESTORE_PROJECT_ID", "").strip() or None
        if project_id:
            return firestore.Client(project=project_id)
        return firestore.Client()
    except Exception:
        return None


def _save_firestore(collection, payload):
    client = _get_firestore_client()
    if client is None:
        return False
    data = dict(payload)
    data["created_at"] = firestore.SERVER_TIMESTAMP
    client.collection(collection).add(data)
    return True


def _list_firestore(collection, limit=10, order_field="created_at"):
    client = _get_firestore_client()
    if client is None:
        return []
    docs = (
        client.collection(collection)
        .order_by(order_field, direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    rows = []
    for doc in docs:
        item = doc.to_dict() or {}
        created_at = item.get("created_at") or timezone.now()
        item["created_at"] = created_at
        item["converted_at"] = item.get("converted_at", created_at)
        rows.append(type("Doc", (), item))
    return rows


def _count_firestore(collection):
    client = _get_firestore_client()
    if client is None:
        return None
    return sum(1 for _ in client.collection(collection).stream())


def chatbot_page(request):
    return render(request, "ai_chat/chatbot.html")


@csrf_exempt
def save_chat_lead(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payload = {
                "session_id": data.get("session_id", ""),
                "name": data.get("name", ""),
                "email": data.get("email", ""),
                "phone": data.get("phone", ""),
                "company": data.get("company", ""),
                "message": data.get("message", ""),
                "source": "chatbot",
            }
            if not _save_firestore("chat_leads", payload):
                ChatLead.objects.create(**payload)
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"error": "Metodo POST necessario"}, status=400)


def chat_analytics(request):
    total_conversations = _count_firestore("chat_history")
    total_conversions = _count_firestore("chat_conversions")
    total_leads = _count_firestore("chat_leads")

    if total_conversations is None:
        total_conversations = ChatHistory.objects.count()
        total_conversions = ChatConversion.objects.count()
        total_leads = ChatLead.objects.count()
        conversions_source = list(ChatConversion.objects.all())
        recent_conversations = ChatHistory.objects.all()[:10]
        recent_conversions = ChatConversion.objects.all()[:10]
        recent_leads = ChatLead.objects.all()[:10]
    else:
        conversions_source = _list_firestore("chat_conversions", limit=200)
        recent_conversations = _list_firestore("chat_history", limit=10)
        recent_conversions = _list_firestore("chat_conversions", limit=10)
        recent_leads = _list_firestore("chat_leads", limit=10)

    conversions_by_type = {}
    for conv in conversions_source:
        conv_type = getattr(conv, "conversion_type", "") or "unknown"
        conversions_by_type[conv_type] = conversions_by_type.get(conv_type, 0) + 1

    context = {
        "total_conversations": total_conversations,
        "total_conversions": total_conversions,
        "total_leads": total_leads,
        "conversions_by_type": conversions_by_type,
        "recent_conversations": recent_conversations,
        "recent_conversions": recent_conversions,
        "recent_leads": recent_leads,
    }
    return render(request, "ai_chat/analytics.html", context)


@csrf_exempt
def chatbot_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").lower().strip()
            session_id = data.get("session_id", str(uuid.uuid4()))

            history_payload = {
                "session_id": session_id,
                "user_message": user_message,
                "bot_response": "Processando...",
            }
            if not _save_firestore("chat_history", history_payload):
                ChatHistory.objects.create(**history_payload)

            if any(
                word in user_message
                for word in [
                    "o que",
                    "explica",
                    "definicao",
                    "significa",
                    "e um erp",
                    "erp e",
                    "o que e erp",
                    "explicar erp",
                    "defina erp",
                    "erp significa",
                    "como funciona erp",
                    "para que serve erp",
                    "vantagens erp",
                ]
            ):
                resposta = """Um ERP (Enterprise Resource Planning) e um sistema integrado de gestao empresarial que unifica todos os processos de uma organizacao em uma unica plataforma.

Principais beneficios:
- Centralizacao de dados e processos
- Automacao de tarefas repetitivas
- Relatorios em tempo real
- Melhoria na tomada de decisoes
- Integracao entre departamentos (vendas, compras, estoque, financeiro)

O Fthec sistemas e automacao e um ERP inteligente com chatbot integrado para transformar seu negocio!"""
            elif any(
                word in user_message
                for word in [
                    "adquirir",
                    "comprar",
                    "contratar",
                    "contato",
                    "comercial",
                    "como conseguir",
                    "quero",
                    "interessado",
                    "demonstracao",
                    "preco",
                    "custo",
                    "orcamento",
                    "citar",
                    "cotacao",
                    "implementar",
                    "instalar",
                    "comecar",
                    "usar",
                    "teste",
                    "avaliacao",
                    "proposta",
                    "negocio",
                    "venda",
                    "cliente",
                    "empresa",
                    "negociar",
                    "fechar negocio",
                ]
            ):
                conversion_payload = {
                    "session_id": session_id,
                    "user_message": user_message,
                    "conversion_type": "demo_request",
                }
                if not _save_firestore("chat_conversions", conversion_payload):
                    ChatConversion.objects.create(**conversion_payload)

                resposta = """Excelente! Para adquirir o Fthec sistemas e automacao para sua empresa, nossa equipe comercial esta pronta para ajudar.

Como prosseguir:
1. Preencha o formulario de inscricao em nossa pagina principal
2. Nossa equipe entrara em contato em ate 24h
3. Recebera uma demonstracao personalizada
4. Orcamento detalhado sem compromisso

<button class="btn btn-primary btn-sm agendar-demo" onclick="window.location.href='/inscricao/'">Fale com especialista</button>

Acesse /inscricao/ ou clique no botao acima para comecar!"""
            else:
                resposta = """Ola! Sou especialista em ERP. Posso explicar o que e um ERP ou ajudar voce a entrar em contato com nossa equipe comercial para adquirir o Fthec sistemas e automacao.

Pergunte sobre:
- "O que e um ERP?" - explicacao completa
- "Como adquirir um ERP?" - contato comercial"""

            final_history_payload = {
                "session_id": session_id,
                "user_message": user_message,
                "bot_response": resposta,
            }
            if not _save_firestore("chat_history", final_history_payload):
                chat_entry = ChatHistory.objects.filter(session_id=session_id).last()
                if chat_entry:
                    chat_entry.bot_response = resposta
                    chat_entry.save()

            return JsonResponse({"response": resposta, "session_id": session_id, "error": False})
        except Exception as e:
            return JsonResponse({"response": f"Erro: {str(e)}", "error": True})

    return JsonResponse({"error": "Metodo POST necessario"}, status=400)
