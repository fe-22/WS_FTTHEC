// Chatbot functionality
function toggleChatbot() {
    const chatbot = document.getElementById('chatbotContainer');
    chatbot.style.display = chatbot.style.display === 'flex' ? 'none' : 'flex';
    
    // Focus on input when opening
    if (chatbot.style.display === 'flex') {
        setTimeout(() => {
            document.getElementById('chatInput').focus();
        }, 100);
    }
}

function handleChatInputKey(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    input.value = '';
    
    // Show typing indicator
    const typingIndicator = addTypingIndicator();
    
    try {
        // Send to Django backend
        const response = await fetch('/chat/send/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ message: message })
        });
        
        // Remove typing indicator
        typingIndicator.remove();
        
        if (response.ok) {
            const data = await response.json();
            addMessage(data.response, 'bot');
        } else {
            addMessage('Desculpe, estou com problemas para responder. Por favor, entre em contato pelo telefone (11) 99999-9999', 'bot');
        }
    } catch (error) {
        typingIndicator.remove();
        addMessage('Erro de conexão. Verifique sua internet ou entre em contato pelo WhatsApp.', 'bot');
    }
}

function addMessage(text, sender) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.textContent = text;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addTypingIndicator() {
    const messagesContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = '<i class="fas fa-ellipsis-h"></i> Digitando...';
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return typingDiv;
}

// CSRF token helper for Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Predefined responses for demo (when OpenAI not available)
const predefinedResponses = {
    'oi': 'Olá! Como posso ajudar sua empresa hoje?',
    'olá': 'Olá! Como posso ajudar sua empresa hoje?',
    'erp': 'Nosso ERP completo inclui controle de estoque, vendas, financeiro, clientes, relatórios e módulo fiscal. Gostaria de saber mais sobre algum módulo específico?',
    'moderloja': 'O ModerLoja é nosso sistema específico para varejo, com PDV avançado, loja virtual integrada e conexão com marketplaces.',
    'preço': 'Temos diferentes planos conforme o tamanho da sua empresa. Posso conectar você com um de nossos consultores para uma cotação personalizada.',
    'demonstração': 'Excelente! Para agendar uma demonstração gratuita, clique no botão "Demonstração Gratuita" no menu ou me informe seu nome e telefone que entraremos em contato.',
    'estoque': 'Nosso módulo de estoque oferece controle em tempo real, inventário automático, alertas de reposição e integração total com vendas e compras.',
    'pdv': 'O PDV (Ponto de Venda) permite vendas rápidas, múltiplas formas de pagamento, emissão de NFC-e, controle de comissões e fechamento de caixa automatizado.'
};