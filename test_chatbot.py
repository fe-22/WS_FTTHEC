import requests
import json

mensagens_teste = ['Olá', 'o que é um erp', 'Como adquirir']

print("🤖 Testando Chatbot...\n")

for msg in mensagens_teste:
    data = {'message': msg, 'session_id': 'test_session'}
    r = requests.post('http://127.0.0.1:8000/ai_chat/api/', json=data)
    if r.status_code == 200:
        resultado = r.json()
        print(f'✅ Mensagem: "{msg}"')
        print(f'   Resposta: {resultado["response"][:100]}...\n')
    else:
        print(f'❌ Erro ao enviar "{msg}": Status {r.status_code}\n')
