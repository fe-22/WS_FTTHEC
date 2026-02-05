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
                
                # 2. ENVIAR EMAIL (só se configurado)
                try:
                    # Verificar se email está configurado
                    if hasattr(settings, 'EMAIL_BACKEND'):
                        print("✉️ Tentando enviar email...")  # Debug
                        
                        # Email para ADMIN
                        send_mail(
                            subject=f'[FTT HEC] Nova Inscrição - {nome}',
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
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'contato@ftthec.com'),
                            recipient_list=[getattr(settings, 'ADMIN_EMAIL', 'seu_email@gmail.com')],  # ALTERE PARA SEU EMAIL
                            fail_silently=True,  # Não quebrar se falhar
                        )
                        
                        # Email para CLIENTE (opcional)
                        send_mail(
                            subject='Confirmação de Inscrição - Fthec',
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
                            Equipe Fthec
                            ''',
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'contato@ftthec.com'),
                            recipient_list=[email],
                            fail_silently=True,
                        )
                        
                        print("✅ Emails enviados com sucesso!")  # Debug
                    else:
                        print("⚠️ EMAIL_BACKEND não configurado")  # Debug
                        
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