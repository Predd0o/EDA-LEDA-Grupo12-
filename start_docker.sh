#!/bin/bash
set -e

IMAGE_NAME="eda-leda-benchmark"
CONTAINER_NAME="eda-leda-benchmark-dev"

if ! command -v docker &> /dev/null; then
    echo "Docker não está instalado."
    echo "Instale em: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! pgrep -x "Docker" > /dev/null; then
        open -a Docker
        echo "Aguardando Docker ficar pronto..."
        for i in {1..30}; do
            docker ps &> /dev/null && break
            sleep 1
        done
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]] && ! systemctl is-active --quiet docker 2>/dev/null; then
    echo "Iniciando daemon Docker..."
    sudo systemctl start docker 2>/dev/null || echo "AVISO: verifique as permissões do Docker"
    sleep 2
fi

if ! docker ps &> /dev/null; then
    echo "Não consegui conectar ao Docker"
    exit 1
fi

if ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
    echo "Imagem $IMAGE_NAME não encontrada. Construindo..."
    docker build -f setup/Dockerfile -t "$IMAGE_NAME" .
fi

docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

docker run -it --rm \
    --name "$CONTAINER_NAME" \
    -v "$(pwd)/data:/workspace/data" \
    -v "$(pwd)/results:/workspace/results" \
    -v "$(pwd)/scripts:/workspace/scripts" \
    "$IMAGE_NAME" \
    /bin/bash
