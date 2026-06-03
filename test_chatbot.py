import requests


def main():
    mensagens_teste = ["Ola", "o que e um erp", "Como adquirir"]

    print("Testando Chatbot...\n")

    for msg in mensagens_teste:
        data = {"message": msg, "session_id": "test_session"}
        response = requests.post(
            "http://127.0.0.1:8000/ai_chat/api/",
            json=data,
            timeout=20,
        )
        if response.status_code == 200:
            resultado = response.json()
            print(f'Mensagem: "{msg}"')
            print(f'   Resposta: {resultado["response"][:100]}...\n')
        else:
            print(f'Erro ao enviar "{msg}": Status {response.status_code}\n')


if __name__ == "__main__":
    main()
