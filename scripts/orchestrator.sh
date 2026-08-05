#!/bin/bash
set -euo pipefail
shopt -s nullglob

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="${BASE_DIR}/data"
RESULTS_DIR="${BASE_DIR}/results"

RUST="${BASE_DIR}/segtree_rust/target/release/segtree_rust"
CPP="${BASE_DIR}/segtree_cpp/build/segtree_cpp"
JAVA="java -cp ${BASE_DIR}/segtree_java Main"
PYTHON="python3 ${BASE_DIR}/segtree_python/main.py"

SIZES="${1:-1000 10000 100000 1000000}"
DISTRIBUTIONS="${2:-random sorted nearly_sorted duplicates all_equal}"
MULS="${3:-1 5 10}"
REPETITIONS="${4:-30}"

mkdir -p "$DATA_DIR" "$RESULTS_DIR"

if [ ! -s "${RESULTS_DIR}/results.csv" ]; then
    echo "language,n,m,load,input_file,ops_executed,op,time_ns,nodes_visited" \
        > "${RESULTS_DIR}/results.csv"
fi

echo "Gerando arquivos de entrada..."
for n in $SIZES; do
    for dist in $DISTRIBUTIONS; do
        for mul in $MULS; do
            m=$((n * mul))
            python3 "${BASE_DIR}/scripts/gen_input.py" --n "$n" --m "$m" --seed 42 \
                --distribution "$dist" --load query --output "${DATA_DIR}/"

            python3 "${BASE_DIR}/scripts/gen_input.py" --n "$n" --m "$m" --seed 42 \
                --distribution "$dist" --load update --output "${DATA_DIR}/"

            python3 "${BASE_DIR}/scripts/gen_input.py" --n "$n" --m "$m" --seed 42 \
                --distribution "$dist" --load mixed \
                --query-ratio 0.5 --update-range-ratio 0.25 \
                --output "${DATA_DIR}/"

            echo "  Gerado: n=${n} m=${m} dist=${dist} (query/update/mixed_5050)"
        done
    done
done

echo "Rodando benchmarks..."

declare -A BINS
for lang in rust cpp java python; do
    case "$lang" in
        rust)
            if [ -x "$RUST" ]; then
                BINS[rust]="$RUST"
            fi
            ;;
        cpp)
            if [ -x "$CPP" ]; then
                BINS[cpp]="$CPP"
            fi
            ;;
        java)
            if [ -f "${BASE_DIR}/segtree_java/Main.class" ]; then
                BINS[java]="$JAVA"
            fi
            ;;
        python)
            py_script="${PYTHON#python3 }"
            if [ -f "$py_script" ]; then
                BINS[python]="$PYTHON"
            fi
            ;;
    esac
    if [ -z "${BINS[$lang]:-}" ]; then
        echo "AVISO: binário/script não encontrado para $lang, pulando" >&2
    fi
done

for lang in "${!BINS[@]}"; do
    bin="${BINS[$lang]}"
    echo "=== $lang ==="
    for n in $SIZES; do
        for dist in $DISTRIBUTIONS; do
            for mul in $MULS; do
                m=$((n * mul))
                for load in query update mixed; do
                    if [ "$load" = "mixed" ]; then
                        input="${DATA_DIR}/input_n${n}_m${m}_s42_${dist}_mixed_5050.txt"
                    else
                        input="${DATA_DIR}/input_n${n}_m${m}_s42_${dist}_${load}.txt"
                    fi

                    if [ ! -f "$input" ]; then
                        echo "  AVISO: arquivo não encontrado, pulando: $input" >&2
                        continue
                    fi

                    $bin --input "$input" --load "$load" \
                        --repetitions "$REPETITIONS" \
                        >> "${RESULTS_DIR}/results.csv"

                    echo "  OK: $lang $(basename "$input") $load"
                done
            done
        done
    done
done

echo "Pronto! Resultados em ${RESULTS_DIR}/results.csv"
