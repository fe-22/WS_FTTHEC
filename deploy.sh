#!/bin/bash

# Script para deploy no Google Cloud Run
# Uso: ./deploy.sh [PROJECT_ID]

set -e

PROJECT_ID=${1:-"your-project-id"}
SERVICE_NAME="ws-fthec"
REGION="southamerica-east1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Iniciando deploy do WS_FTTHEC no Google Cloud Run"
echo "📍 Projeto: ${PROJECT_ID}"
echo "🌎 Região: ${REGION}"
echo "🏷️  Serviço: ${SERVICE_NAME}"

# Verificar se gcloud está instalado e configurado
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI não encontrado. Instale o Google Cloud SDK primeiro."
    exit 1
fi

# Verificar se está logado
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 > /dev/null; then
    echo "❌ Você não está logado no gcloud. Execute: gcloud auth login"
    exit 1
fi

# Configurar projeto
echo "🔧 Configurando projeto: ${PROJECT_ID}"
gcloud config set project ${PROJECT_ID}

# Habilitar APIs necessárias
echo "🔌 Habilitando APIs necessárias..."
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build e push da imagem
echo "🏗️  Building e fazendo push da imagem Docker..."
gcloud builds submit --tag ${IMAGE_NAME}:latest .

# Deploy no Cloud Run
echo "🚀 Fazendo deploy no Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars DEBUG=False,DJANGO_SETTINGS_MODULE=erp_site.settings \
    --set-secrets OPENAI_API_KEY=OPENAI_API_KEY:latest \
    --set-secrets SECRET_KEY=SECRET_KEY:latest

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")

echo ""
echo "✅ Deploy concluído com sucesso!"
echo "🌐 URL do serviço: ${SERVICE_URL}"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure as secrets OPENAI_API_KEY e SECRET_KEY no Google Cloud Secret Manager"
echo "2. Teste o chatbot em: ${SERVICE_URL}/ai_chat/"
echo "3. Verifique os logs: gcloud logs read --service=${SERVICE_NAME} --region=${REGION}"