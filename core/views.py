import datetime
import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import redirect, render

from .models import Inscricao


def home(request):
    """Pagina inicial - Landing Page"""
    return render(request, "home.html")


def inscricao_view(request):
    """Processa formulario de contato/inscricao"""
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        empresa = request.POST.get("empresa", "").strip()
        cargo = request.POST.get("cargo", "").strip()
        mensagem = request.POST.get("mensagem", "").strip()

        if not nome:
            messages.error(request, "O nome e obrigatorio.")
        elif not email:
            messages.error(request, "O e-mail e obrigatorio.")
        else:
            try:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if getattr(settings, "LEADS_CSV_ENABLED", True):
                    leads_csv_path = Path(settings.LEADS_CSV_PATH)
                    leads_csv_path.parent.mkdir(parents=True, exist_ok=True)
                    with leads_csv_path.open("a", encoding="utf-8") as csv_file:
                        csv_file.write(
                            f"{timestamp},{nome},{email},{telefone},{empresa},{cargo},{mensagem}\n"
                        )

                Inscricao.objects.create(
                    nome=nome,
                    email=email,
                    telefone=telefone,
                    empresa=empresa,
                    cargo=cargo,
                    mensagem=mensagem,
                )

                email_backend = getattr(
                    settings,
                    "EMAIL_BACKEND",
                    "django.core.mail.backends.console.EmailBackend",
                )

                if email_backend != "django.core.mail.backends.console.EmailBackend":
                    try:
                        send_mail(
                            subject=f"[FTHEC] Nova Inscricao - {nome}",
                            message=f"""
                            NOVA INSCRICAO/LEAD RECEBIDO

                            Nome: {nome}
                            Email: {email}
                            Telefone: {telefone}
                            Empresa: {empresa}
                            Cargo: {cargo}
                            Mensagem: {mensagem}

                            Data/Hora: {timestamp}
                            """,
                            from_email=getattr(
                                settings, "DEFAULT_FROM_EMAIL", "fthec@fthec.com.br"
                            ),
                            recipient_list=[
                                getattr(settings, "ADMIN_EMAIL", "fthec@fthec.com.br")
                            ],
                            fail_silently=False,
                        )

                        send_mail(
                            subject="Confirmacao de Inscricao - FTHEC",
                            message=f"""
                            Ola {nome},

                            Recebemos sua inscricao com sucesso.

                            Nossa equipe entrara em contato em breve.

                            Dados recebidos:
                            - Nome: {nome}
                            - Email: {email}
                            - Telefone: {telefone}

                            Atenciosamente,
                            Equipe FTHEC
                            """,
                            from_email=getattr(
                                settings, "DEFAULT_FROM_EMAIL", "fthec@fthec.com.br"
                            ),
                            recipient_list=[email],
                            fail_silently=False,
                        )
                    except Exception:
                        pass

                messages.success(
                    request,
                    f"Obrigado {nome}. Sua inscricao foi recebida com sucesso.",
                )
                return redirect("home")
            except Exception as exc:
                messages.error(request, f"Erro no processamento: {exc}")

    return render(request, "inscricao.html")


@login_required
def crm_view(request):
    """CRM de inscricoes e mensagens de leads."""
    leads = Inscricao.objects.order_by("-data_inscricao")
    query = request.GET.get("q", "").strip()
    if query:
        leads = leads.filter(
            Q(nome__icontains=query)
            | Q(email__icontains=query)
            | Q(empresa__icontains=query)
            | Q(cargo__icontains=query)
            | Q(mensagem__icontains=query)
        )
    context = {
        "leads": leads,
        "query": query,
    }
    return render(request, "crm.html", context)


def dashboard_demo(request):
    """Pagina de demonstracao do Dashboard do ERP"""
    receitas_despesas = [
        {"mes": "Jan", "receitas": 125000, "despesas": 95000},
        {"mes": "Fev", "receitas": 132000, "despesas": 98000},
        {"mes": "Mar", "receitas": 148000, "despesas": 102000},
        {"mes": "Abr", "receitas": 156000, "despesas": 108000},
        {"mes": "Mai", "receitas": 142000, "despesas": 105000},
        {"mes": "Jun", "receitas": 168000, "despesas": 112000},
    ]
    dashboard_data = {
        "vendas_hoje": 15420.50,
        "vendas_mes": 387650.80,
        "pedidos_pendentes": 23,
        "clientes_ativos": 1247,
        "produtos_estoque_baixo": 8,
        "ticket_medio": 482.40,
        "sla_atendimento": 96,
        "receitas_despesas": receitas_despesas,
        "chart_labels": json.dumps([item["mes"] for item in receitas_despesas]),
        "chart_receitas": json.dumps([item["receitas"] for item in receitas_despesas]),
        "chart_despesas": json.dumps([item["despesas"] for item in receitas_despesas]),
        "produtos_mais_vendidos": [
            {"nome": "Produto A", "vendas": 245, "receita": 12250.00},
            {"nome": "Produto B", "vendas": 189, "receita": 9450.00},
            {"nome": "Produto C", "vendas": 156, "receita": 7800.00},
            {"nome": "Produto D", "vendas": 134, "receita": 6700.00},
            {"nome": "Produto E", "vendas": 98, "receita": 4900.00},
        ],
        "pipeline": [
            {"etapa": "Leads", "volume": 328, "cor": "primary"},
            {"etapa": "Qualificados", "volume": 146, "cor": "info"},
            {"etapa": "Propostas", "volume": 64, "cor": "warning"},
            {"etapa": "Fechados", "volume": 23, "cor": "success"},
        ],
    }
    return render(request, "demo/dashboard.html", dashboard_data)


def pdv_demo(request):
    """Pagina de demonstracao do PDV"""
    pdv_data = {
        "produtos": [
            {"codigo": "001", "nome": "Produto A", "preco": 25.90, "estoque": 45},
            {"codigo": "002", "nome": "Produto B", "preco": 15.50, "estoque": 32},
            {"codigo": "003", "nome": "Produto C", "preco": 89.90, "estoque": 12},
            {"codigo": "004", "nome": "Produto D", "preco": 45.00, "estoque": 28},
            {"codigo": "005", "nome": "Produto E", "preco": 12.99, "estoque": 67},
        ],
        "carrinho": [
            {"produto": "Produto A", "qtd": 2, "preco_unit": 25.90, "total": 51.80},
            {"produto": "Produto C", "qtd": 1, "preco_unit": 89.90, "total": 89.90},
        ],
        "total_carrinho": 141.70,
        "formas_pagamento": [
            "Dinheiro",
            "Cartao de Credito",
            "Cartao de Debito",
            "PIX",
            "Cheque",
        ],
    }
    return render(request, "demo/pdv.html", pdv_data)


def financeiro_demo(request):
    """Modelo de dashboard financeiro"""
    fluxo_caixa = [
        {"semana": "S1", "entrada": 78000, "saida": 52000},
        {"semana": "S2", "entrada": 84000, "saida": 61000},
        {"semana": "S3", "entrada": 91000, "saida": 64000},
        {"semana": "S4", "entrada": 102000, "saida": 69000},
    ]
    context = {
        "mrr": 126400,
        "inadimplencia": 2.8,
        "caixa_disponivel": 284000,
        "margem_ebitda": 18.5,
        "fluxo_labels": json.dumps([item["semana"] for item in fluxo_caixa]),
        "fluxo_entrada": json.dumps([item["entrada"] for item in fluxo_caixa]),
        "fluxo_saida": json.dumps([item["saida"] for item in fluxo_caixa]),
        "contas": [
            {"titulo": "Folha e encargos", "valor": 48500, "status": "Pago"},
            {"titulo": "Infraestrutura cloud", "valor": 12200, "status": "Hoje"},
            {"titulo": "Marketing performance", "valor": 18900, "status": "Em 2 dias"},
            {"titulo": "Comissoes comerciais", "valor": 22400, "status": "Em 5 dias"},
        ],
    }
    return render(request, "demo/financeiro.html", context)


def operacoes_demo(request):
    """Modelo de dashboard operacional"""
    produtividade = [
        {"turno": "06h", "ordens": 14},
        {"turno": "09h", "ordens": 19},
        {"turno": "12h", "ordens": 17},
        {"turno": "15h", "ordens": 24},
        {"turno": "18h", "ordens": 21},
    ]
    context = {
        "otif": 97.2,
        "tempo_medio": 38,
        "retrabalho": 1.9,
        "ocupacao": 81,
        "prod_labels": json.dumps([item["turno"] for item in produtividade]),
        "prod_valores": json.dumps([item["ordens"] for item in produtividade]),
        "equipes": [
            {"nome": "Expedicao", "meta": 94, "realizado": 98},
            {"nome": "Separacao", "meta": 91, "realizado": 89},
            {"nome": "Suprimentos", "meta": 88, "realizado": 92},
            {"nome": "Atendimento", "meta": 95, "realizado": 97},
        ],
        "alertas": [
            "3 pedidos com risco de atraso nas proximas 2 horas",
            "Dock 04 com o maior giro do dia",
            "Equipe de atendimento com SLA acima da meta",
        ],
    }
    return render(request, "demo/operacoes.html", context)
