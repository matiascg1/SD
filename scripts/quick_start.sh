set -e  # Salir si hay algún error

echo "=========================================="
echo "  Sistema de Análisis Yahoo! Answers"
echo "  Script de Inicio Rápido"
echo "=========================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' 

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "1. Verificando Docker..."
if command -v docker &> /dev/null; then
    print_success "Docker está instalado"
else
    print_error "Docker no está instalado"
    echo "   Instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "2. Verificando Docker Compose..."
if command -v docker-compose &> /dev/null; then
    print_success "Docker Compose está instalado"
else
    print_error "Docker Compose no está instalado"
    echo "   Instala Docker Compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "3. Verificando archivo .env..."
if [ -f ".env" ]; then
    print_success "Archivo .env encontrado"
    
    if grep -q "LLM_PROVIDER=GEMINI" .env; then
        if grep -q "GEMINI_API_KEY=tu_api_key_aqui" .env || grep -q "GEMINI_API_KEY=$" .env; then
            print_warning "GEMINI_API_KEY no está configurada"
            echo "   Edita el archivo .env y agrega tu API key de Google Gemini"
            echo "   Obtén tu API key en: https://makersuite.google.com/app/apikey"
        else
            print_success "GEMINI_API_KEY está configurada"
        fi
    fi
else
    print_error "Archivo .env no encontrado"
    exit 1
fi

echo "4. Verificando dataset..."
DATA_PATH=$(grep "^DATA_PATH=" .env | cut -d '=' -f2)
if [ -z "$DATA_PATH" ]; then
    DATA_PATH="data/test.csv"
fi

if [ -f "$DATA_PATH" ]; then
    print_success "Dataset encontrado en $DATA_PATH"
else
    print_error "Dataset no encontrado en $DATA_PATH"
    echo "   Descarga el dataset de Yahoo! Answers desde:"
    echo "   https://www.kaggle.com/datasets/jarupula/yahoo-answers-dataset"
    echo "   Y colócalo en $DATA_PATH"
    exit 1
fi

echo "5. Verificando directorio data/..."
if [ ! -d "data" ]; then
    mkdir -p data
    print_success "Directorio data/ creado"
else
    print_success "Directorio data/ existe"
fi

echo ""
echo "=========================================="
echo "Configuración verificada correctamente"
echo "=========================================="
echo ""
read -p "¿Deseas iniciar el sistema ahora? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo ""
    echo "Iniciando sistema con Docker Compose..."
    echo "Presiona Ctrl+C para detener el sistema"
    echo ""
    docker-compose up --build
else
    echo ""
    echo "Para iniciar el sistema manualmente, ejecuta:"
    echo "  docker-compose up --build"
    echo ""
    echo "O usa el Makefile:"
    echo "  make up"
    echo ""
fi
