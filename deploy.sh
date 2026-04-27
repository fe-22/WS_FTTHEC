#!/bin/bash

# Deploy Cloud Run (source deploy) para Django + Cloud SQL.
# Uso:
#   ./deploy.sh PROJECT_ID DOMAIN CLOUD_SQL_CONNECTION_NAME [REGION] [SERVICE_NAME]
# Exemplo:
#   ./deploy.sh meu-projeto fthec.com.br meu-projeto:southamerica-east1:erp-db southamerica-east1 ws-fthec

set -euo pipefail

PROJECT_ID="${1:-}"
DOMAIN="${2:-}"
CLOUD_SQL_CONNECTION_NAME="${3:-}"
REGION="${4:-southamerica-east1}"
SERVICE_NAME="${5:-ws-fthec}"

if [[ -z "${PROJECT_ID}" || -z "${DOMAIN}" || -z "${CLOUD_SQL_CONNECTION_NAME}" ]]; then
  echo "Uso: ./deploy.sh PROJECT_ID DOMAIN CLOUD_SQL_CONNECTION_NAME [REGION] [SERVICE_NAME]"
  exit 1
fi

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud CLI nao encontrado. Instale o Google Cloud SDK."
  exit 1
fi

if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 >/dev/null; then
  echo "Voce nao esta logado no gcloud. Execute: gcloud auth login"
  exit 1
fi

echo "Iniciando deploy no Cloud Run"
echo "Projeto: ${PROJECT_ID}"
echo "Regiao: ${REGION}"
echo "Servico: ${SERVICE_NAME}"
echo "Dominio: ${DOMAIN}"
echo "Cloud SQL: ${CLOUD_SQL_CONNECTION_NAME}"

gcloud config set project "${PROJECT_ID}"

echo "Habilitando APIs"
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  sqladmin.googleapis.com

echo "Verificando segredos obrigatorios"
gcloud secrets describe SECRET_KEY >/dev/null 2>&1 || {
  echo "Secret SECRET_KEY nao encontrado."
  echo "Crie com: echo -n 'sua_chave' | gcloud secrets create SECRET_KEY --replication-policy=automatic --data-file=-"
  exit 1
}
gcloud secrets describe DB_PASSWORD >/dev/null 2>&1 || {
  echo "Secret DB_PASSWORD nao encontrado."
  echo "Crie com: echo -n 'sua_senha' | gcloud secrets create DB_PASSWORD --replication-policy=automatic --data-file=-"
  exit 1
}
if ! gcloud secrets describe OPENAI_API_KEY >/dev/null 2>&1; then
  echo "Aviso: secret OPENAI_API_KEY nao encontrado. O chatbot pode falhar sem ele."
fi

ALLOWED_HOSTS="${DOMAIN},www.${DOMAIN}"
CSRF_TRUSTED_ORIGINS="https://${DOMAIN},https://www.${DOMAIN}"
CORS_ALLOWED_ORIGINS="${CSRF_TRUSTED_ORIGINS}"
DB_HOST="/cloudsql/${CLOUD_SQL_CONNECTION_NAME}"

echo "Deploying source para Cloud Run"
if gcloud secrets describe OPENAI_API_KEY >/dev/null 2>&1; then
  gcloud run deploy "${SERVICE_NAME}" \
    --source . \
    --region "${REGION}" \
    --allow-unauthenticated \
    --add-cloudsql-instances "${CLOUD_SQL_CONNECTION_NAME}" \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "DEBUG=False,DJANGO_SETTINGS_MODULE=erp_site.settings,ALLOWED_HOSTS=${ALLOWED_HOSTS},CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS},CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS},DB_HOST=${DB_HOST},DB_PORT=3306,DB_NAME=erp_fthec,DB_USER=root,USE_X_FORWARDED_HOST=True,SECURE_SSL_REDIRECT=True" \
    --set-secrets "SECRET_KEY=SECRET_KEY:latest,DB_PASSWORD=DB_PASSWORD:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest"
else
  gcloud run deploy "${SERVICE_NAME}" \
    --source . \
    --region "${REGION}" \
    --allow-unauthenticated \
    --add-cloudsql-instances "${CLOUD_SQL_CONNECTION_NAME}" \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars "DEBUG=False,DJANGO_SETTINGS_MODULE=erp_site.settings,ALLOWED_HOSTS=${ALLOWED_HOSTS},CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS},CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS},DB_HOST=${DB_HOST},DB_PORT=3306,DB_NAME=erp_fthec,DB_USER=root,USE_X_FORWARDED_HOST=True,SECURE_SSL_REDIRECT=True" \
    --set-secrets "SECRET_KEY=SECRET_KEY:latest,DB_PASSWORD=DB_PASSWORD:latest"
fi

SERVICE_URL="$(gcloud run services describe "${SERVICE_NAME}" --region="${REGION}" --format='value(status.url)')"

echo ""
echo "Deploy concluido."
echo "URL do servico: ${SERVICE_URL}"
echo "Teste: ${SERVICE_URL}/ai_chat/"
