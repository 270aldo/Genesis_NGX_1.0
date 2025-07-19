#!/bin/bash
# Script para configurar Google Cloud Project para NGX RAG Implementation con Vertex AI Search

set -e

echo "🚀 Configurando Google Cloud para NGX RAG Implementation con Vertex AI Search..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar si gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI no está instalado. Por favor instálalo primero:${NC}"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Variables de configuración - usar las existentes del .env si están disponibles
PROJECT_ID=${GCP_PROJECT_ID:-$(grep GCP_PROJECT_ID .env 2>/dev/null | cut -d '=' -f2 || echo "ngx-agents-rag")}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_ACCOUNT_NAME="ngx-rag-service"
BUCKET_NAME="${PROJECT_ID}-knowledge-base"
SEARCH_APP_ID="ngx-fitness-search"
SEARCH_LOCATION="global"

echo -e "${YELLOW}📋 Configuración:${NC}"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Account: $SERVICE_ACCOUNT_NAME"
echo "Bucket: $BUCKET_NAME"
echo "Vertex AI Search App: $SEARCH_APP_ID"
echo ""

# Función para verificar si un API está habilitado
check_api() {
    local api=$1
    if gcloud services list --enabled --project=$PROJECT_ID | grep -q "$api"; then
        echo -e "${GREEN}✓ $api ya está habilitado${NC}"
        return 0
    else
        return 1
    fi
}

# 1. Configurar proyecto
echo -e "${YELLOW}1. Configurando proyecto...${NC}"
gcloud config set project $PROJECT_ID 2>/dev/null || {
    echo -e "${RED}❌ Error: El proyecto $PROJECT_ID no existe.${NC}"
    echo "Por favor, crea el proyecto primero o actualiza GCP_PROJECT_ID en tu .env"
    exit 1
}

# 2. Habilitar APIs necesarias
echo -e "${YELLOW}2. Habilitando APIs necesarias...${NC}"

APIS=(
    "aiplatform.googleapis.com"           # Vertex AI
    "discoveryengine.googleapis.com"      # Vertex AI Search
    "storage.googleapis.com"              # Cloud Storage
    "secretmanager.googleapis.com"        # Secret Manager
    "cloudresourcemanager.googleapis.com" # Resource Manager
    "iam.googleapis.com"                  # IAM
    "compute.googleapis.com"              # Compute Engine
)

for api in "${APIS[@]}"; do
    if ! check_api "$api"; then
        echo -e "${YELLOW}Habilitando $api...${NC}"
        gcloud services enable $api --project=$PROJECT_ID
    fi
done

# 3. Crear Service Account (si no existe)
echo -e "${YELLOW}3. Configurando Service Account...${NC}"
SA_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if ! gcloud iam service-accounts describe $SA_EMAIL --project=$PROJECT_ID &>/dev/null; then
    echo "Creando service account..."
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="NGX RAG Service Account" \
        --project=$PROJECT_ID
else
    echo -e "${GREEN}✓ Service account ya existe${NC}"
fi

# 4. Asignar roles necesarios
echo -e "${YELLOW}4. Asignando roles IAM...${NC}"

ROLES=(
    "roles/aiplatform.user"                    # Vertex AI User
    "roles/discoveryengine.admin"              # Vertex AI Search Admin
    "roles/storage.admin"                      # Storage Admin
    "roles/secretmanager.secretAccessor"       # Secret Accessor
)

for role in "${ROLES[@]}"; do
    echo "Asignando $role..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="$role" \
        --quiet
done

# 5. Crear bucket para Knowledge Base
echo -e "${YELLOW}5. Creando Cloud Storage bucket...${NC}"
if ! gsutil ls -b gs://$BUCKET_NAME &>/dev/null; then
    echo "Creando bucket $BUCKET_NAME..."
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME/
    
    # Crear estructura de carpetas
    echo "Creando estructura de carpetas..."
    echo "# NGX Knowledge Base" | gsutil cp - gs://$BUCKET_NAME/README.md
    echo "# Fitness Knowledge" | gsutil cp - gs://$BUCKET_NAME/fitness/README.md
    echo "# Nutrition Knowledge" | gsutil cp - gs://$BUCKET_NAME/nutrition/README.md
    echo "# Wellness Knowledge" | gsutil cp - gs://$BUCKET_NAME/wellness/README.md
    echo "# User Data" | gsutil cp - gs://$BUCKET_NAME/user_data/README.md
else
    echo -e "${GREEN}✓ Bucket ya existe${NC}"
fi

# 6. Información sobre Vertex AI Search
echo -e "${YELLOW}6. Configuración de Vertex AI Search...${NC}"
echo -e "${YELLOW}ℹ️  Vertex AI Search se debe configurar manualmente en la consola:${NC}"
echo "   1. Ve a https://console.cloud.google.com/gen-app-builder"
echo "   2. Crea una nueva aplicación de búsqueda"
echo "   3. Selecciona 'Search' como tipo"
echo "   4. Configura el data store con el bucket: gs://$BUCKET_NAME"
echo "   5. Anota el ID de la aplicación y el data store"

# 7. Crear archivo de configuración de entorno
echo -e "${YELLOW}7. Actualizando archivo de configuración .env.rag...${NC}"
cat > .env.rag << EOF
# Google Cloud Configuration for RAG
GCP_PROJECT_ID=$PROJECT_ID
GCP_REGION=$REGION

# Vertex AI Settings
VERTEX_AI_LOCATION=$REGION
EMBEDDING_MODEL=text-embedding-large-exp-03-07
GENERATION_MODEL=gemini-2.0-flash-exp

# Vertex AI Search Configuration
VERTEX_SEARCH_LOCATION=$SEARCH_LOCATION
VERTEX_SEARCH_APP_ID=$SEARCH_APP_ID
VERTEX_SEARCH_DATASTORE_ID=ngx-fitness-datastore

# Storage Configuration
GCS_KNOWLEDGE_BASE_BUCKET=$BUCKET_NAME

# RAG Configuration
RAG_ENABLED=true
VECTOR_DIMENSIONS=3072
CHUNK_SIZE=512
CHUNK_OVERLAP=50
MAX_SEARCH_RESULTS=5
SIMILARITY_THRESHOLD=0.7

# Model Parameters
TEMPERATURE=0.3
MAX_OUTPUT_TOKENS=8192
TOP_P=0.8
TOP_K=40

# Search Configuration
SEARCH_QUERY_MODEL=text-bison@002
ENABLE_SPELL_CORRECTION=true
ENABLE_SUMMARIZATION=true
SEARCH_TIER=SEARCH_TIER_ENTERPRISE
EOF

# 8. Crear estructura de directorios para RAG
echo -e "${YELLOW}8. Creando estructura de directorios RAG...${NC}"
mkdir -p rag/{embeddings,search,generation,knowledge_base/{fitness,nutrition,wellness},utils}
touch rag/__init__.py
touch rag/embeddings/__init__.py
touch rag/search/__init__.py
touch rag/generation/__init__.py
touch rag/utils/__init__.py

# 9. Mostrar próximos pasos
echo -e "${GREEN}✅ Configuración inicial completada!${NC}"
echo ""
echo -e "${YELLOW}📝 Próximos pasos:${NC}"
echo "1. Configura Vertex AI Search en la consola:"
echo "   https://console.cloud.google.com/gen-app-builder?project=$PROJECT_ID"
echo ""
echo "2. Actualiza .env.rag con los IDs de tu Search App y Datastore"
echo ""
echo "3. Añade las variables de .env.rag a tu archivo .env principal"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
echo "- Vertex AI Search tiene un período de prueba gratuito"
echo "- Los embeddings se facturan por caracteres procesados"
echo "- Revisa los precios en: https://cloud.google.com/vertex-ai/pricing"
echo ""
echo -e "${GREEN}✨ Listo para implementar RAG con Vertex AI Search!${NC}"