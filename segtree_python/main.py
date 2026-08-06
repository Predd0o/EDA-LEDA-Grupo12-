import argparse
import sys
import time

from segment_tree import SegmentTree

class Op:
    """Classe base para as operações"""
    pass

class QuerySum(Op):
    def __init__(self, l, r):
        self.l = l
        self.r = r

class QueryMin(Op):
    def __init__(self, l, r):
        self.l = l
        self.r = r

class QueryMax(Op):
    def __init__(self, l, r):
        self.l = l
        self.r = r

class UpdateRange(Op):
    def __init__(self, l, r, value):
        self.l = l
        self.r = r
        self.value = value

class UpdatePoint(Op):
    def __init__(self, index, value):
        self.index = index
        self.value = value

def parse_input(path):
    """Lê o arquivo de entrada gerado pelo gen_input.py"""
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{path}' não encontrado.", file=sys.stderr)
        sys.exit(1)

    if not lines:
        raise ValueError("Arquivo de entrada vazio")

    # Linha 1: N e M
    header = lines[0].split()
    n = int(header[0])
    m = int(header[1])

    # Linha 2: Valores do array
    values_line = lines[1]
    values = [int(x) for x in values_line.split()[:n]]

    # Linha 3 em diante: Operações
    ops = []
    for line in lines[2:]:
        tokens = line.split()
        if not tokens:
            continue
        
        op_type = tokens[0]
        if op_type == "query":
            l = int(tokens[1])
            r = int(tokens[2])
            # 1 leitura de query vira 3 chamadas na árvore
            ops.append(QuerySum(l, r))
            ops.append(QueryMin(l, r))
            ops.append(QueryMax(l, r))
        elif op_type == "update_range":
            l = int(tokens[1])
            r = int(tokens[2])
            value = int(tokens[3])
            ops.append(UpdateRange(l, r, value))
        elif op_type == "update_point":
            index = int(tokens[1])
            value = int(tokens[2])
            ops.append(UpdatePoint(index, value))

    return n, m, values, ops

def load_operations(load, all_ops):
    """Filtra as operações caso o parâmetro --load seja passado"""
    if load == "query":
        return [op for op in all_ops if isinstance(op, (QuerySum, QueryMin, QueryMax))]
    elif load == "update":
        return [op for op in all_ops if isinstance(op, (UpdateRange, UpdatePoint))]
    elif load == "mixed":
        return all_ops
    else:
        raise ValueError("Parâmetro --load inválido: use query, update, ou mixed")

def emit(language, n, m, load, input_file, ops_executed, op_type, time_ns, primitives):
    """Imprime no exato formato CSV esperado e pelo Orquestrador"""
    print(f"{language},{n},{m},{load},{input_file},{ops_executed},{op_type},{time_ns},{primitives}")

def main():
    parser = argparse.ArgumentParser(description="Main da Segment Tree em Python")
    parser.add_argument("--input", type=str, required=True, help="Caminho do arquivo de entrada")
    parser.add_argument("--load", type=str, default="query", help="Tipo de carga (query, update, mixed)")
    parser.add_argument("--repetitions", type=int, default=1, help="Repetições cronometradas")

    args = parser.parse_args()

    n, m, values, all_ops = parse_input(args.input)
    load_ops = load_operations(args.load, all_ops)
    ops_executed = len(load_ops)

    # Aquecimento (Warmup): Executa 5 vezes para esquentar o interpretador sem medir o tempo
    for _ in range(5):
        segtree = SegmentTree(values)
        for op in load_ops:
            if isinstance(op, QuerySum):
                segtree.query_sum(op.l, op.r)
            elif isinstance(op, QueryMin):
                segtree.query_min(op.l, op.r)
            elif isinstance(op, QueryMax):
                segtree.query_max(op.l, op.r)
            elif isinstance(op, UpdateRange):
                segtree.update_range(op.l, op.r, op.value)
            elif isinstance(op, UpdatePoint):
                segtree.update_point(op.index, op.value)

    # Repetições oficiais cronometradas
    for _ in range(args.repetitions):
        
        # 1. Medindo a construção da árvore
        build_start = time.perf_counter_ns()
        segtree = SegmentTree(values)
        build_time = time.perf_counter_ns() - build_start
        
        # Como o build também visita nós, pegamos o contador dele
        build_primitives = segtree.get_counter()
        
        emit("python", n, m, args.load, args.input, ops_executed, "build", build_time, build_primitives)

        # 2. Medindo o tempo e os nós visitados de todas as operações da lista

        # Zera o contador antes de rodar as operações
        segtree.reset_counter()
            
        # Dispara cronômetro antes do for que percorre todas as operações
        start = time.perf_counter_ns()

        for op in load_ops:
            
            if isinstance(op, QuerySum):
                segtree.query_sum(op.l, op.r)
            elif isinstance(op, QueryMin):
                segtree.query_min(op.l, op.r)
            elif isinstance(op, QueryMax):
                segtree.query_max(op.l, op.r)
            elif isinstance(op, UpdateRange):
                segtree.update_range(op.l, op.r, op.value)
            elif isinstance(op, UpdatePoint):
                segtree.update_point(op.index, op.value)
                
        # Para cronômetro após todas as operações
        time_spent = time.perf_counter_ns() - start
            
        # Pega quantos nós foram visitados em todas as operações
        primitives_count = segtree.get_counter()
            
        emit("python", n, m, args.load, args.input, ops_executed, "batch_ops", time_spent, primitives_count)

if __name__ == "__main__":
    main()