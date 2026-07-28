#!/bin/bash
set -e

IMAGE_NAME="segdtree-bench"

echo "==> Building Docker image..."
docker build -f setup/Dockerfile -t "${IMAGE_NAME}" .

echo ""
echo "==> Image built successfully: ${IMAGE_NAME}"
echo ""
echo "To run benchmarks:"
echo "  docker run --rm \\"
echo "    --cpus=4 \\"
echo "    --memory=4g \\"
echo "    -v \"\$(pwd)/data:/data\" \\"
echo "    -v \"\$(pwd)/scripts:/scripts\" \\"
echo "    -v \"\$(pwd)/segtree_rust:/segtree_rust\" \\"
echo "    ${IMAGE_NAME} \\"
echo "    python3 /scripts/orchestrator.py --size 100000 --ops 1000 --load query"