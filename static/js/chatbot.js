console.log("🤖 chatbot.js INICIADO - Versão Debug");

document.addEventListener("DOMContentLoaded", function() {
    console.log("✅ DOM pronto");
    
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");
    const chatMessages = document.getElementById("chat-messages");
    
    console.log("Elementos encontrados:", {
        input: userInput ? "✅" : "❌",
        button: sendButton ? "✅" : "❌",
        messages: chatMessages ? "✅" : "❌"
    });
    
    if (!userInput || !sendButton) {
        console.warn("⚠️ Não está na página do chatbot");
        return;
    }
    
    // Gera session_id único para esta sessão
    let sessionId = localStorage.getItem('chatbot_session_id');
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('chatbot_session_id', sessionId);
    }
    console.log("Session ID:", sessionId);
    
    // FUNÇÃO PRINCIPAL
    async function enviarMensagem() {
        const mensagem = userInput.value.trim();
        if (!mensagem) return;
        
        console.log("📤 Enviando:", mensagem);
        
        // Adiciona mensagem do usuário
        const userDiv = document.createElement("div");
        userDiv.className = "alert alert-primary";
        userDiv.innerHTML = `<strong>Você:</strong> ${mensagem}`;
        chatMessages.appendChild(userDiv);
        
        userInput.value = "";
        
        try {
            // Envia para API
            const response = await fetch("/ai_chat/api/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")?.value || ""
                },
                body: JSON.stringify({ 
                    message: mensagem,
                    session_id: sessionId 
                })
            });
            
            const data = await response.json();
            console.log("📥 Resposta API:", data);
            
            // Adiciona resposta do bot
            const botDiv = document.createElement("div");
            botDiv.className = data.error ? "alert alert-danger" : "alert alert-success";
            botDiv.innerHTML = `<strong>Assistente:</strong> ${data.response}`;
            chatMessages.appendChild(botDiv);
            
            // Adiciona event listener para botões de ação na resposta
            const actionButtons = botDiv.querySelectorAll('.agendar-demo');
            actionButtons.forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log("🎯 Botão Agendar clicado - Tracking conversão");
                    
                    // Tracking do clique
                    fetch("/ai_chat/lead/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")?.value || ""
                        },
                        body: JSON.stringify({
                            session_id: sessionId,
                            action: 'button_click',
                            button_type: 'agendar_demo'
                        })
                    }).then(() => {
                        window.location.href = '/inscricao/';
                    });
                });
            });
            
        } catch (error) {
            console.error("❌ Erro:", error);
            const errorDiv = document.createElement("div");
            errorDiv.className = "alert alert-warning";
            errorDiv.innerHTML = `<strong>Erro:</strong> Não foi possível conectar ao servidor.`;
            chatMessages.appendChild(errorDiv);
        }
        
        // Rola para baixo
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Event Listeners
    sendButton.addEventListener("click", enviarMensagem);
    userInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter") enviarMensagem();
    });
    
    // Botões rápidos
    document.querySelectorAll(".quick-question").forEach(btn => {
        btn.addEventListener("click", function() {
            userInput.value = this.getAttribute("data-question");
            enviarMensagem();
        });
    });
    
    console.log("✅ Chatbot configurado e pronto!");
    userInput.focus();
});
