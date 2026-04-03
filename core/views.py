from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
import datetime

def home(request):
    """Página inicial - Landing Page"""
    return render(request, "home.html")

def inscricao_view(request):
    """Processa formulário de contato/inscrição"""
    if request.method == "POST":
        # Captura todos os dados do formulário
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        empresa = request.POST.get("empresa", "").strip()
        cargo = request.POST.get("cargo", "").strip()
        mensagem = request.POST.get("mensagem", "").strip()
        
        # Validação básica
        if not nome:
            messages.error(request, "❌ O nome é obrigatório!")
        elif not email:
            messages.error(request, "❌ O e-mail é obrigatório!")
        else:
            try:
                # 1. SALVAR NO CSV (backup)
                with open("leads.csv", "a", encoding="utf-8") as f:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"{timestamp},{nome},{email},{telefone},{empresa},{cargo},{mensagem}\n")
                
                print(f"📁 Lead salvo no CSV: {nome}, {email}")  # Debug
                
                # 2. ENVIAR EMAIL
                try:
                    email_backend = getattr(settings, 'EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
                    print(f"✉️ EMAIL_BACKEND atual: {email_backend}")  # Debug

                    if email_backend == 'django.core.mail.backends.console.EmailBackend':
                        print("⚠️ Modo console ativado. Emails serão apenas logados, não enviados.")
                    else:
                        print("✉️ Tentando enviar emails reais via SMTP...")

                        # Email para ADMIN
                        send_mail(
                            subject=f'[FTHEC] Nova Inscrição - {nome}',
                            message=f'''
                            📋 NOVA INSCRIÇÃO/LEAD RECEBIDO

                            👤 Nome: {nome}
                            📧 Email: {email}
                            📞 Telefone: {telefone}
                            🏢 Empresa: {empresa}
                            💼 Cargo: {cargo}
                            💬 Mensagem: {mensagem}

                            ⏰ Data/Hora: {timestamp}
                            📁 Backup: Salvo em leads.csv
                            ''',
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'fthec@fthec.com.br'),
                            recipient_list=[getattr(settings, 'ADMIN_EMAIL', 'fthec@fthec.com.br')],
                            fail_silently=False,
                        )

                        # Email para CLIENTE
                        send_mail(
                            subject='Confirmação de Inscrição - FTHEC',
                            message=f'''
                            Olá {nome},

                            ✅ Recebemos sua inscrição com sucesso!

                            Agradecemos seu interesse em nossos serviços.
                            Nossa equipe entrará em contato em breve.

                            📧 Dados recebidos:
                            • Nome: {nome}
                            • Email: {email}
                            • Telefone: {telefone}

                            Atenciosamente,
                            Equipe FTHEC
                            ''',
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'fthec@fthec.com.br'),
                            recipient_list=[email],
                            fail_silently=False,
                        )

                        print("✅ Emails enviados com sucesso!")

                except Exception as email_error:
                    print(f"⚠️ Erro no envio de email (não crítico): {email_error}")
                    # Não mostra erro para o usuário, apenas loga
                
                # 3. Mensagem de sucesso para o usuário
                messages.success(request, f"✅ Obrigado {nome}! Inscrição realizada com sucesso. Em breve entraremos em contato.")
                return redirect("home")
                
            except Exception as e:
                print(f"❌ Erro crítico: {e}")  # Debug
                messages.error(request, f"❌ Erro no processamento: {str(e)}")
    
    # Se GET ou erro, mostra a página de inscrição
    return render(request, "inscricao.html")

def dashboard_demo(request):
    """Página de demonstração do Dashboard do ERP"""
    # Dados de exemplo para o dashboard
    dashboard_data = {
        'vendas_hoje': 15420.50,
        'vendas_mes': 387650.80,
        'pedidos_pendentes': 23,
        'clientes_ativos': 1247,
        'produtos_estoque_baixo': 8,
        'receitas_despesas': [
            {'mes': 'Jan', 'receitas': 125000, 'despesas': 95000},
            {'mes': 'Fev', 'receitas': 132000, 'despesas': 98000},
            {'mes': 'Mar', 'receitas': 148000, 'despesas': 102000},
            {'mes': 'Abr', 'receitas': 156000, 'despesas': 108000},
            {'mes': 'Mai', 'receitas': 142000, 'despesas': 105000},
            {'mes': 'Jun', 'receitas': 168000, 'despesas': 112000},
        ],
        'produtos_mais_vendidos': [
            {'nome': 'Produto A', 'vendas': 245, 'receita': 12250.00},
            {'nome': 'Produto B', 'vendas': 189, 'receita': 9450.00},
            {'nome': 'Produto C', 'vendas': 156, 'receita': 7800.00},
            {'nome': 'Produto D', 'vendas': 134, 'receita': 6700.00},
            {'nome': 'Produto E', 'vendas': 98, 'receita': 4900.00},
        ]
    }
    return render(request, "demo/dashboard.html", dashboard_data)

def pdv_demo(request):
    """Página de demonstração do PDV (Ponto de Venda)"""
    # Dados de exemplo para o PDV
    pdv_data = {
        'produtos': [
            {'codigo': '001', 'nome': 'Produto A', 'preco': 25.90, 'estoque': 45},
            {'codigo': '002', 'nome': 'Produto B', 'preco': 15.50, 'estoque': 32},
            {'codigo': '003', 'nome': 'Produto C', 'preco': 89.90, 'estoque': 12},
            {'codigo': '004', 'nome': 'Produto D', 'preco': 45.00, 'estoque': 28},
            {'codigo': '005', 'nome': 'Produto E', 'preco': 12.99, 'estoque': 67},
        ],
        'carrinho': [
            {'produto': 'Produto A', 'qtd': 2, 'preco_unit': 25.90, 'total': 51.80},
            {'produto': 'Produto C', 'qtd': 1, 'preco_unit': 89.90, 'total': 89.90},
        ],
        'total_carrinho': 141.70,
        'formas_pagamento': ['Dinheiro', 'Cartão de Crédito', 'Cartão de Débito', 'PIX', 'Cheque']
    }
    return render(request, "demo/pdv.html", pdv_data)