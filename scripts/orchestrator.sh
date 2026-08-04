#!/bin/bash
set -euo pipefail
shopt -s nullglob

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="${BASE_DIR}/data"
RESULTS_DIR="${BASE_DIR}/results"

RUST="${BASE_DIR}/segtree_rust/target/release/segtree_rust"
CPP="${BASE_DIR}/segtree_cpp/build/segtree_cpp"
JAVA="java -jar ${BASE_DIR}/segtree_java/target/segtree.jar"
PYTHON="python3 ${BASE_DIR}/segtree_python/main.py"

SIZES="${1:-100 1000 10000 100000 1000000}"
DISTRIBUTIONS="${2:-random sorted nearly_sorted}"
WARMUP="${3:-1}"
REPETITIONS="${4:-3}"

mkdir -p "$DATA_DIR" "$RESULTS_DIR"

echo "language,n,m,load,input_file,ops_executed,op,time_ns,nodes_visited" \
    > "${RESULTS_DIR}/results.csv"

echo "Gerando arquivos de entrada..."
for n in $SIZES; do
    for dist in $DISTRIBUTIONS; do
        python3 "${BASE_DIR}/scripts/gen_input.py" --n "$n" --seed 42 \
            --distribution "$dist" --load query --output "${DATA_DIR}/"

        python3 "${BASE_DIR}/scripts/gen_input.py" --n "$n" --seed 42 \
            --distribution "$dist" --load update --output "${DATA_DIR}/"

        python3 "${BASE_DIR}/scripts/gen_input.py" --n "$n" --seed 42 \
            --distribution "$dist" --load mixed \
            --query-ratio 0.5 --update-range-ratio 0.25 \
            --output "${DATA_DIR}/"

        echo "  Gerado: n=${n} dist=${dist} (query/update/mixed_5050)"
    done
done

echo "Rodando benchmarks..."
for lang in rust cpp java python; do
    echo "=== $lang ==="
    for n in $SIZES; do
        for dist in $DISTRIBUTIONS; do
            for load in query update mixed; do
                if [ "$load" = "mixed" ]; then
                    input="${DATA_DIR}/input_n${n}_s42_${dist}_mixed_5050.txt"
                else
                    input="${DATA_DIR}/input_n${n}_s42_${dist}_${load}.txt"
                fi

                if [ ! -f "$input" ]; then
                    echo "  AVISO: arquivo não encontrado, pulando: $input" >&2
                    continue
                fi

                case "$lang" in
                    rust)   bin="$RUST" ;;
                    cpp)    bin="$CPP" ;;
                    java)   bin="$JAVA" ;;
                    python) bin="$PYTHON" ;;
                esac

                $bin --input "$input" --load "$load" \
                    --warmup "$WARMUP" --repetitions "$REPETITIONS" \
                    >> "${RESULTS_DIR}/results.csv"

                echo "  OK: $lang $(basename "$input") $load"
            done
        done
    done
done

echo "Pronto! Resultados em ${RESULTS_DIR}/results.csv"