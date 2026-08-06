#!/bin/bash

# Script para iniciar Docker e entrar em um container do projeto
# Suporta: macOS, Linux e Windows (WSL2/Git Bash)

set -e

IMAGE_NAME="eda-leda-benchmark"
CONTAINER_NAME="eda-leda-benchmark-dev"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir com cores
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# ============================================
# 1. Verificar se Docker está instalado
# ============================================
log_info "Verificando se Docker está instalado..."
if ! command -v docker &> /dev/null; then
    log_error "Docker não está instalado."
    echo "Instale em: https://www.docker.com/products/docker-desktop"
    exit 1
fi
log_success "Docker encontrado"

# ============================================
# 2. Iniciar Docker conforme o SO
# ============================================
log_info "Iniciando Docker..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! pgrep -x "Docker" > /dev/null; then
        log_info "Abrindo Docker Desktop..."
        open -a Docker
        log_info "Aguardando Docker ficar pronto (até 30s)..."
        for i in {1..30}; do
            if docker ps &> /dev/null; then
                log_success "Docker pronto!"
                break
            fi
            sleep 1
        done
    else
        log_success "Docker já está rodando"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if ! systemctl is-active --quiet docker 2>/dev/null; then
        log_info "Iniciando daemon Docker..."
        sudo systemctl start docker 2>/dev/null || log_warning "Verifique permissões do Docker"
        sleep 2
    fi
    log_success "Docker pronto"
else
    # Windows (WSL2/Git Bash)
    log_warning "Windows detectado - certifique-se de que Docker Desktop está aberto"
fi

# ============================================
# 3. Verificar conexão com Docker
# ============================================
if ! docker ps &> /dev/null; then
    log_error "Não consegui conectar ao Docker"
    exit 1
fi
log_success "Conexão com Docker OK"

# ============================================
# 4. Construir imagem se não existir
# ============================================
echo ""
log_info "Verificando imagem Docker..."

if ! docker image inspect "${IMAGE_NAME}" &> /dev/null; then
    log_warning "Imagem '${IMAGE_NAME}' não encontrada. Construindo..."
    echo ""
    
    if docker build -f setup/Dockerfile -t "${IMAGE_NAME}" .; then
        log_success "Imagem construída com sucesso"
    else
        log_error "Falha ao construir a imagem"
        exit 1
    fi
else
    log_success "Imagem '${IMAGE_NAME}' encontrada"
fi

# ============================================
# 5. Remover container antigo (se existir)
# ============================================
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log_info "Removendo container anterior..."
    docker rm -f "${CONTAINER_NAME}" &> /dev/null || true
fi

# ============================================
# 6. Iniciar e entrar no container
# ============================================
echo ""
echo "════════════════════════════════════════════════"
echo -e "${GREEN}🐳 Iniciando container interativo${NC}"
echo "════════════════════════════════════════════════"
echo ""

docker run -it --rm \
    --name "${CONTAINER_NAME}" \
    -v "$(pwd)/data:/workspace/data" \
    -v "$(pwd)/results:/workspace/results" \
    -v "$(pwd)/scripts:/workspace/scripts" \
    "${IMAGE_NAME}" \
    /bin/bash

# ============================================
# 7. Mensagem final
# ============================================
echo ""
log_success "Container finalizado"
echo "Até logo! 👋"
