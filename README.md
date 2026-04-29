# WS_FTTHEC - ERP Inteligente com IA

Sistema ERP completo com chatbot integrado para automação empresarial.

## 🚀 Deploy no Google Cloud Run

### Pré-requisitos

1. **Google Cloud SDK** instalado e configurado
2. **Docker** instalado
3. **Conta Google Cloud** com projeto criado
4. **APIs habilitadas**: Cloud Run, Artifact Registry, Cloud Build

### Configuração Inicial

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/fe-22/WS_FTTHEC.git
   cd WS_FTTHEC
   ```

2. **Configure o projeto Google Cloud:**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   gcloud auth login
   ```

3. **Crie secrets para variáveis sensíveis:**
   ```bash
   # OPENAI_API_KEY
   echo -n "your-openai-api-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

   # SECRET_KEY do Django
   echo -n "your-django-secret-key" | gcloud secrets create SECRET_KEY --data-file=-
   ```

### Deploy Automático

Execute o script de deploy:

```bash
chmod +x deploy.sh
./deploy.sh YOUR_PROJECT_ID SEU_DOMINIO CLOUD_SQL_CONNECTION_NAME [REGION] [SERVICE_NAME]
```

### Deploy Manual

Se preferir fazer manualmente (Artifact Registry):

```bash
# Defina variaveis
PROJECT_ID="YOUR_PROJECT_ID"
REGION="southamerica-east1"
AR_REPO="ws-fthec"
SERVICE_NAME="ws-fthec"

# Crie o repositorio Docker no Artifact Registry (uma vez)
gcloud artifacts repositories create "$AR_REPO" \
  --repository-format=docker \
  --location="$REGION" \
  --description="Docker images for $SERVICE_NAME"

# Build e push da imagem no Artifact Registry
gcloud builds submit \
  --tag "$REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/$SERVICE_NAME:latest" .

# Deploy no Cloud Run
gcloud run deploy ws-fthec \
    --image "$REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/$SERVICE_NAME:latest" \
    --platform managed \
    --region southamerica-east1 \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars DEBUG=False,DJANGO_SETTINGS_MODULE=erp_site.settings \
    --set-secrets OPENAI_API_KEY=OPENAI_API_KEY:latest \
    --set-secrets SECRET_KEY=SECRET_KEY:latest
```

### Verificação do Deploy

1. **Obter URL do serviço:**
   ```bash
   gcloud run services describe ws-fthec --region=southamerica-east1 --format="value(status.url)"
   ```

2. **Testar o chatbot:**
   - Acesse: `https://SEU_URL/ai_chat/`
   - Teste as mensagens: "Olá", "O que é um ERP?", "Como adquirir"

3. **Verificar logs:**
   ```bash
   gcloud logs read --service=ws-fthec --region=southamerica-east1
   ```

## 🔧 Configurações Técnicas

### Ambiente de Produção
- **Runtime:** Python 3.11
- **Framework:** Django 4.2.7
- **Banco:** SQLite (para desenvolvimento) / PostgreSQL (produção recomendada)
- **Cache:** Whitenoise para arquivos estáticos
- **CORS:** Configurado para permitir requisições do frontend

### Variáveis de Ambiente
- `DEBUG=False` - Modo produção
- `DJANGO_SETTINGS_MODULE=erp_site.settings`
- `OPENAI_API_KEY` - Chave da API OpenAI
- `SECRET_KEY` - Chave secreta do Django

### URLs Importantes
- **Home:** `/`
- **Chatbot:** `/ai_chat/`
- **Analytics:** `/ai_chat/analytics/`
- **Admin:** `/admin/`

## 🐛 Troubleshooting

### Chatbot não responde
1. Verifique se as migrations foram executadas
2. Confirme se a OPENAI_API_KEY está configurada
3. Verifique logs: `gcloud logs read`

### Erro 500
1. Verifique configurações de CORS
2. Confirme se STATIC_URL está correto
3. Verifique DEBUG=False em produção

### Problemas de CORS
- Certifique-se que `django-cors-headers` está instalado
- Verifique `CORS_ALLOWED_ORIGINS` no settings.py

## 📊 Monitoramento

### Métricas importantes:
- **Uptime do serviço**
- **Latência de resposta**
- **Taxa de erro**
- **Conversões do chatbot**

### Logs:
```bash
# Logs em tempo real
gcloud logs read --service=ws-fthec --region=southamerica-east1 --follow

# Logs de erro
gcloud logs read --service=ws-fthec --region=southamerica-east1 --filter="severity>=ERROR"
```

## 🔄 Atualizações

Para atualizar o serviço após mudanças no código:

```bash
git add .
git commit -m "Atualização do sistema"
git push
./deploy.sh YOUR_PROJECT_ID
./deploy.sh YOUR_PROJECT_ID SEU_DOMINIO CLOUD_SQL_CONNECTION_NAME [REGION] [SERVICE_NAME]
```

---

**Desenvolvido por:** FTHEC Sistemas & Automações
**Data:** Abril 2026
