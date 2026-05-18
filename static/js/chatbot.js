console.log("chatbot.js iniciado - debug");

document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM pronto");

    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");
    const chatMessages = document.getElementById("chat-messages");

    console.log("Elementos encontrados:", {
        input: userInput ? "ok" : "erro",
        button: sendButton ? "ok" : "erro",
        messages: chatMessages ? "ok" : "erro",
    });

    if (!userInput || !sendButton || !chatMessages) {
        console.warn("Nao esta na pagina do chatbot");
        return;
    }

    let sessionId = localStorage.getItem("chatbot_session_id");
    if (!sessionId) {
        sessionId = `session_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`;
        localStorage.setItem("chatbot_session_id", sessionId);
    }
    console.log("Session ID:", sessionId);

    function buildApiUrl(path) {
        const normalized = path.startsWith("/") ? path : `/${path}`;
        return `${window.location.origin}${normalized}`;
    }

    async function enviarMensagem() {
        const mensagem = userInput.value.trim();
        if (!mensagem) return;

        console.log("Enviando:", mensagem);

        const userDiv = document.createElement("div");
        userDiv.className = "alert alert-primary";
        userDiv.innerHTML = `<strong>Voce:</strong> ${mensagem}`;
        chatMessages.appendChild(userDiv);

        userInput.value = "";

        const typingDiv = document.createElement("div");
        typingDiv.className = "alert alert-secondary";
        typingDiv.innerHTML = "<strong>Assistente:</strong> Processando...";
        chatMessages.appendChild(typingDiv);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        try {
            const response = await fetch(buildApiUrl("/ai_chat/api/"), {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken":
                        document.querySelector("[name=csrfmiddlewaretoken]")?.value || "",
                },
                signal: controller.signal,
                body: JSON.stringify({
                    message: mensagem,
                    session_id: sessionId,
                }),
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`Falha no servidor (${response.status}).`);
            }

            const contentType = response.headers.get("content-type") || "";
            if (!contentType.includes("application/json")) {
                throw new Error("Resposta invalida do servidor.");
            }

            const data = await response.json();
            console.log("Resposta API:", data);

            typingDiv.remove();

            const botDiv = document.createElement("div");
            botDiv.className = data.error ? "alert alert-danger" : "alert alert-success";
            botDiv.innerHTML = `<strong>Assistente:</strong> ${data.response}`;
            chatMessages.appendChild(botDiv);

            const actionButtons = botDiv.querySelectorAll(".agendar-demo");
            actionButtons.forEach((button) => {
                button.addEventListener("click", function (e) {
                    e.preventDefault();
                    console.log("Botao Agendar clicado - tracking conversao");

                    fetch(buildApiUrl("/ai_chat/lead/"), {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken":
                                document.querySelector("[name=csrfmiddlewaretoken]")?.value || "",
                        },
                        body: JSON.stringify({
                            session_id: sessionId,
                            action: "button_click",
                            button_type: "agendar_demo",
                        }),
                    }).finally(() => {
                        window.location.href = "/inscricao/";
                    });
                });
            });
        } catch (error) {
            clearTimeout(timeoutId);
            typingDiv.remove();
            console.error("Erro:", error);

            const errorDiv = document.createElement("div");
            errorDiv.className = "alert alert-warning";
            if (error.name === "AbortError") {
                errorDiv.innerHTML =
                    "<strong>Erro:</strong> A requisicao demorou demais. Tente novamente.";
            } else {
                errorDiv.innerHTML = `<strong>Erro:</strong> ${error.message || "Nao foi possivel conectar ao servidor."}`;
            }
            chatMessages.appendChild(errorDiv);
        }

        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    sendButton.addEventListener("click", enviarMensagem);
    userInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter") enviarMensagem();
    });

    document.querySelectorAll(".quick-question").forEach((btn) => {
        btn.addEventListener("click", function () {
            userInput.value = this.getAttribute("data-question");
            enviarMensagem();
        });
    });

    console.log("Chatbot configurado e pronto");
    userInput.focus();
});
