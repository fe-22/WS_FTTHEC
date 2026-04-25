import datetime
import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import EmpresaReceita, Inscricao
from .services import (
    build_empresa_queryset,
    discover_public_contacts,
    serialize_empresa,
    sync_receita_filtered_import,
)


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
    if request.method == "POST":
        action = request.POST.get("action", "").strip()
        if action == "sincronizar_receita":
            filtros = {
                "release": request.POST.get("release", "").strip(),
                "data_inicio": request.POST.get("data_inicio", "").strip(),
                "data_fim": request.POST.get("data_fim", "").strip(),
                "segmentos": request.POST.get("segmentos", "").strip(),
                "uf": request.POST.get("uf", "").strip().upper(),
                "municipio": request.POST.get("municipio", "").strip(),
                "municipios": request.POST.get("municipios", "").strip(),
                "situacao_cadastral": request.POST.get("situacao_cadastral", "").strip(),
                "matriz_only": request.POST.get("matriz_only") == "on",
            }
            limit_raw = request.POST.get("limit", "").strip()

            if not any(
                [
                    filtros["data_inicio"],
                    filtros["data_fim"],
                    filtros["segmentos"],
                    filtros["uf"],
                    filtros["municipio"],
                    filtros["municipios"],
                ]
            ):
                messages.error(
                    request,
                    "Informe ao menos um filtro de recorte antes de sincronizar a base Receita.",
                )
                return redirect("crm")

            try:
                limit = int(limit_raw) if limit_raw else 500
                limit = min(max(limit, 1), 5000)
            except ValueError:
                messages.error(request, "Informe um limite numerico valido para a sincronizacao.")
                return redirect("crm")

            try:
                summary = sync_receita_filtered_import(
                    cache_dir=settings.RECEITA_SYNC_CACHE_DIR,
                    release=filtros["release"] or None,
                    data_inicio=filtros["data_inicio"],
                    data_fim=filtros["data_fim"],
                    segmentos=filtros["segmentos"],
                    uf=filtros["uf"],
                    municipio=filtros["municipio"],
                    municipios=filtros["municipios"],
                    situacao_cadastral=filtros["situacao_cadastral"] or "02",
                    matriz_only=filtros["matriz_only"],
                    limit=limit,
                )
                messages.success(
                    request,
                    "Sincronizacao concluida. "
                    f"Referencia: {summary['release']}. "
                    f"Correspondencias: {summary['matched']}. "
                    f"Criados: {summary['created']}. "
                    f"Atualizados: {summary['updated']}.",
                )
            except Exception as exc:
                messages.error(request, f"Falha ao sincronizar base da Receita: {exc}")

            return redirect("crm")

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
        "empresas_count": EmpresaReceita.objects.count(),
        "receita_sync_defaults": {
            "situacao_cadastral": "02",
            "limit": 500,
        },
    }
    return render(request, "crm.html", context)


@login_required
@require_http_methods(["GET"])
def crm_empresas_api(request):
    """API para consulta de empresas importadas da base Receita."""
    queryset = build_empresa_queryset(request.GET)
    total = queryset.count()

    try:
        limit = min(max(int(request.GET.get("limit", 50)), 1), 200)
    except (TypeError, ValueError):
        limit = 50

    try:
        offset = max(int(request.GET.get("offset", 0)), 0)
    except (TypeError, ValueError):
        offset = 0

    empresas = queryset[offset : offset + limit]
    data = {
        "count": total,
        "limit": limit,
        "offset": offset,
        "results": [serialize_empresa(item) for item in empresas],
    }
    return JsonResponse(data)


@login_required
@require_http_methods(["POST"])
def crm_empresa_enriquecer_api(request, empresa_id):
    """Enriquece empresa com contatos comerciais publicos."""
    empresa = get_object_or_404(EmpresaReceita, pk=empresa_id)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = {}

    discover_site = payload.get("discover_site", True)

    try:
        contatos_publicos, source_urls = discover_public_contacts(
            empresa,
            discover_site=discover_site,
        )
    except Exception as exc:
        empresa.enrichment_status = "failed"
        empresa.save(update_fields=["enrichment_status", "updated_at"])
        return JsonResponse(
            {
                "ok": False,
                "error": str(exc),
                "empresa": serialize_empresa(empresa),
            },
            status=502,
        )

    empresa.contatos_publicos = contatos_publicos
    empresa.enrichment_source_urls = source_urls
    empresa.enrichment_status = "done"
    empresa.enrichment_checked_at = datetime.datetime.now(datetime.timezone.utc)

    if not empresa.site_url and source_urls:
        empresa.site_url = source_urls[0]

    if contatos_publicos["emails"] and not empresa.email:
        empresa.email = contatos_publicos["emails"][0]

    if contatos_publicos["telefones"] and not empresa.telefone:
        empresa.telefone = contatos_publicos["telefones"][0]

    empresa.save()

    return JsonResponse(
        {
            "ok": True,
            "empresa": serialize_empresa(empresa),
            "source_urls": source_urls,
        }
    )


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
