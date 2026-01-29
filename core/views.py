from django.shortcuts import render, redirect
from django.contrib import messages
import datetime

def home(request):
    """Página inicial - Landing Page"""
    return render(request, "home.html")

def inscricao_view(request):
    """Processa formulário de contato"""
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        empresa = request.POST.get("empresa", "").strip()
        cargo = request.POST.get("cargo", "").strip()
        mensagem = request.POST.get("mensagem", "").strip()
        
        if not nome:
            messages.error(request, "❌ O nome é obrigatório!")
        elif not email:
            messages.error(request, "❌ O e-mail é obrigatório!")
        else:
            try:
                with open("leads.csv", "a", encoding="utf-8") as f:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"{timestamp},{nome},{email},{telefone},{empresa},{cargo},{mensagem}\\n")
                
                messages.success(request, f"✅ Obrigado {nome}! Entraremos em contato em breve.")
                return redirect("home")
                
            except Exception as e:
                messages.error(request, f"❌ Erro: {str(e)}")
    
    return render(request, "inscricao.html")
