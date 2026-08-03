#!/bin/bash

BASE_DIR="$(dirname "$0")/.."
DATA_DIR="${BASE_DIR}/data"
RESULTS_DIR="${BASE_DIR}/results"

RUST="./segtree_rust/target/release/segtree_rust"
CPP="./segtree_cpp/build/segtree_cpp"
JAVA="java -jar ./segtree_java/target/segtree.jar"
PYTHON="python3 ./segtree_python/main.py"

SIZES="${1:-100 1000 10000 100000 1000000}"
DISTRIBUTIONS="${2:-random sorted nearly_sorted}"
QUERY_RATIOS="${3:-0.5 0.7 0.9}"
WARMUP="${4:-1}"
REPETITIONS="${5:-3}"

mkdir -p "$RESULTS_DIR"

echo "language,n,m,load,input_file,ops_executed,op,time_ns,primitives" \
    > "${RESULTS_DIR}/results.csv"

echo "Gerando arquivos de entrada..."
for n in $SIZES; do
    for dist in $DISTRIBUTIONS; do
        for qr in $QUERY_RATIOS; do
            nome="input_n${n}_s42_${dist}_qr${qr}.txt"
            python3 scripts/gen_input.py --n "$n" --seed 42 \
                --distribution "$dist" --query-ratio "$qr" \
                --output "${DATA_DIR}/${nome}"
            echo "  Gerado: ${nome}"
        done
    done
done

echo "Rodando benchmarks..."
for lang in rust cpp java python; do
    echo "=== $lang ==="
    for input in "${DATA_DIR}"/input_n*.txt; do
        for load in query update mixed; do
            if [ "$lang" = "rust" ]; then
                "$RUST" --input "$input" --load "$load" \
                    --warmup "$WARMUP" --repetitions "$REPETITIONS" \
                    >> "${RESULTS_DIR}/results.csv"
            elif [ "$lang" = "cpp" ]; then
                "$CPP" --input "$input" --load "$load" \
                    --warmup "$WARMUP" --repetitions "$REPETITIONS" \
                    >> "${RESULTS_DIR}/results.csv"
            elif [ "$lang" = "java" ]; then
                $JAVA --input "$input" --load "$load" \
                    --warmup "$WARMUP" --repetitions "$REPETITIONS" \
                    >> "${RESULTS_DIR}/results.csv"
            elif [ "$lang" = "python" ]; then
                "$PYTHON" --input "$input" --load "$load" \
                    --warmup "$WARMUP" --repetitions "$REPETITIONS" \
                    >> "${RESULTS_DIR}/results.csv"
            fi
            echo "  OK: $lang $(basename "$input") $load"
        done
    done
done

echo "Pronto! Resultados em ${RESULTS_DIR}/results.csv"