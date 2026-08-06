import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.StringTokenizer;

/**
 * Programa principal do benchmark da Segment Tree em Java. Lê um arquivo de
 * entrada gerado pelo {@code gen_input.py}, monta a carga de operações de
 * acordo com {@code --load}, executa (opcionalmente) um aquecimento e mede o
 * tempo e a quantidade de "primitivas" (nós visitados) de cada operação,
 * imprimindo os resultados em CSV no formato esperado pelo orquestrador.
 */
public class Main {

    /** Tipos de operação suportados pelo arquivo de entrada. */
    private enum OpType {
        QUERY_SUM, QUERY_MIN, QUERY_MAX, UPDATE_RANGE, UPDATE_POINT
    }

    /**
     * Representa uma única operação a ser executada sobre a Segment Tree.
     * Reúne todos os tipos de operação em uma única classe (em vez de uma
     * hierarquia), já que os campos usados variam pouco entre elas.
     */
    private static final class Op {
        final OpType type;
        final int l;
        final int r;
        final long value;

        private Op(OpType type, int l, int r, long value) {
            this.type = type;
            this.l = l;
            this.r = r;
            this.value = value;
        }

        static Op querySum(int l, int r) {
            return new Op(OpType.QUERY_SUM, l, r, 0);
        }

        static Op queryMin(int l, int r) {
            return new Op(OpType.QUERY_MIN, l, r, 0);
        }

        static Op queryMax(int l, int r) {
            return new Op(OpType.QUERY_MAX, l, r, 0);
        }

        static Op updateRange(int l, int r, long value) {
            return new Op(OpType.UPDATE_RANGE, l, r, value);
        }

        static Op updatePoint(int index, long value) {
            return new Op(OpType.UPDATE_POINT, index, index, value);
        }
    }

    /** Resultado do parsing do arquivo de entrada. */
    private static final class ParsedInput {
        final int n;
        final int m;
        final int[] values;
        final List<Op> ops;

        ParsedInput(int n, int m, int[] values, List<Op> ops) {
            this.n = n;
            this.m = m;
            this.values = values;
            this.ops = ops;
        }
    }

    public static void main(String[] args) {
        String inputPath = parseArg(args, "--input");
        if (inputPath == null) {
            System.err.println("required: --input <path>");
            System.exit(1);
        }
        String loadArg = parseArgOrDefault(args, "--load", "query");
        int warmup = parseArgIntOrDefault(args, "--warmup", 5);
        int repetitions = parseArgIntOrDefault(args, "--repetitions", 1);

        ParsedInput parsed = parseInput(inputPath);
        List<Op> loadOps = loadOperations(loadArg, parsed.ops);
        int opsExecuted = loadOps.size();

        // Aquecimento: executa sem medir, para "esquentar" a JIT.
        for (int w = 0; w < warmup; w++) {
            segmentTree tree = new segmentTree(parsed.values);
            for (Op op : loadOps) {
                execute(tree, op);
            }
        }

        // Repetições oficiais, cronometradas.
        for (int rep = 0; rep < repetitions; rep++) {
            long buildStart = System.nanoTime();
            segmentTree tree = new segmentTree(parsed.values);
            long buildTime = System.nanoTime() - buildStart;
            long buildPrimitives = tree.getCounter();

            emit("java", parsed.n, parsed.m, loadArg, inputPath, opsExecuted, "build", buildTime, buildPrimitives);

            tree.resetCounter();
            long totalStart = System.nanoTime();
            for (Op op : loadOps) {
                execute(tree, op);
            }
            long totalElapsed = System.nanoTime() - totalStart;
            long totalPrimitives = tree.getCounter();
            emit("java", parsed.n, parsed.m, loadArg, inputPath, opsExecuted, "batch_ops", totalElapsed,
                    totalPrimitives);
        }
    }

    /**
     * Executa uma operação sobre a árvore, descartando o valor de retorno das
     * consultas (o objetivo aqui é apenas medir o custo, não usar o resultado).
     *
     * @param tree árvore sobre a qual a operação será executada
     * @param op   operação a ser executada
     */
    private static void execute(segmentTree tree, Op op) {
        switch (op.type) {
            case QUERY_SUM:
                tree.querySum(op.l, op.r);
                break;
            case QUERY_MIN:
                tree.queryMin(op.l, op.r);
                break;
            case QUERY_MAX:
                tree.queryMax(op.l, op.r);
                break;
            case UPDATE_RANGE:
                tree.updateRange(op.l, op.r, op.value);
                break;
            case UPDATE_POINT:
                tree.updatePoint(op.l, op.value);
                break;
        }
    }

    /**
     * Filtra a lista completa de operações de acordo com o tipo de carga
     * solicitado.
     *
     * @param load   tipo de carga: {@code query}, {@code update} ou {@code mixed}
     * @param allOps lista completa de operações lidas do arquivo de entrada
     * @return lista filtrada de operações a serem executadas
     * @throws IllegalArgumentException se {@code load} for inválido
     */
    private static List<Op> loadOperations(String load, List<Op> allOps) {
        List<Op> result = new ArrayList<>();
        switch (load) {
            case "query":
                for (Op op : allOps) {
                    if (op.type == OpType.QUERY_SUM || op.type == OpType.QUERY_MIN || op.type == OpType.QUERY_MAX) {
                        result.add(op);
                    }
                }
                return result;
            case "update":
                for (Op op : allOps) {
                    if (op.type == OpType.UPDATE_RANGE || op.type == OpType.UPDATE_POINT) {
                        result.add(op);
                    }
                }
                return result;
            case "mixed":
                return allOps;
            default:
                throw new IllegalArgumentException("Parâmetro --load inválido: use query, update, ou mixed");
        }
    }

    /**
     * Lê e interpreta o arquivo de entrada gerado por {@code gen_input.py}: a
     * primeira linha contém {@code N} e {@code M}, a segunda contém os {@code N}
     * valores do array e as linhas seguintes descrevem as operações. Cada linha
     * {@code query l r} expande em três operações ({@code query_sum},
     * {@code query_min} e {@code query_max})
     *
     * @param path caminho do arquivo de entrada
     * @return dados de entrada já interpretados
     */
    private static ParsedInput parseInput(String path) {
        try (BufferedReader reader = new BufferedReader(new FileReader(path))) {
            String header = reader.readLine();
            if (header == null) {
                throw new RuntimeException("Arquivo de entrada vazio");
            }
            StringTokenizer headerTok = new StringTokenizer(header);
            int n = Integer.parseInt(headerTok.nextToken());
            int m = Integer.parseInt(headerTok.nextToken());

            String valuesLine = reader.readLine();
            if (valuesLine == null) {
                throw new RuntimeException("Linha de valores ausente");
            }
            int[] values = new int[n];
            StringTokenizer valuesTok = new StringTokenizer(valuesLine);
            for (int i = 0; i < n; i++) {
                values[i] = Integer.parseInt(valuesTok.nextToken());
            }

            List<Op> ops = new ArrayList<>();
            String line;
            while ((line = reader.readLine()) != null) {
                StringTokenizer tok = new StringTokenizer(line);
                if (!tok.hasMoreTokens()) {
                    continue;
                }
                String opType = tok.nextToken();
                switch (opType) {
                    case "Q": {
                        int l = Integer.parseInt(tok.nextToken());
                        int r = Integer.parseInt(tok.nextToken());
                        ops.add(Op.querySum(l, r));
                        ops.add(Op.queryMin(l, r));
                        ops.add(Op.queryMax(l, r));
                        break;
                    }
                    case "U": {
                        int l = Integer.parseInt(tok.nextToken());
                        int r = Integer.parseInt(tok.nextToken());
                        long value = Long.parseLong(tok.nextToken());
                        ops.add(Op.updateRange(l, r, value));
                        break;
                    }
                    case "update_point": {
                        int index = Integer.parseInt(tok.nextToken());
                        long value = Long.parseLong(tok.nextToken());
                        ops.add(Op.updatePoint(index, value));
                        break;
                    }
                    default:
                        // Linha desconhecida: ignorada, igual às versões Python e Rust.
                        break;
                }
            }

            return new ParsedInput(n, m, values, ops);
        } catch (IOException e) {
            System.err.println("Erro: não foi possível abrir o arquivo '" + path + "': " + e.getMessage());
            System.exit(1);
            throw new RuntimeException(e); // inalcançável, apenas para satisfazer o compilador
        }
    }

    /**
     * Imprime uma linha de resultado no formato CSV esperado pelo orquestrador.
     */
    private static void emit(String language, int n, int m, String load, String inputFile, int opsExecuted,
            String op, long timeNs, long primitives) {
        System.out.println(language + "," + n + "," + m + "," + load + "," + inputFile + "," + opsExecuted + ","
                + op + "," + timeNs + "," + primitives);
    }

    /**
     * Procura o valor associado a uma flag de linha de comando (ex.:
     * {@code --input caminho}).
     *
     * @param args lista de argumentos
     * @param flag nome da flag, incluindo os hífens (ex.: {@code "--input"})
     * @return valor associado, ou {@code null} se a flag não foi passada
     */
    private static String parseArg(String[] args, String flag) {
        for (int i = 0; i < args.length; i++) {
            if (args[i].equals(flag) && i + 1 < args.length) {
                return args[i + 1];
            }
        }
        return null;
    }

    private static String parseArgOrDefault(String[] args, String flag, String defaultValue) {
        String value = parseArg(args, flag);
        return value != null ? value : defaultValue;
    }

    private static int parseArgIntOrDefault(String[] args, String flag, int defaultValue) {
        String value = parseArg(args, flag);
        if (value == null) {
            return defaultValue;
        }
        try {
            return Integer.parseInt(value);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("invalid " + flag, e);
        }
    }
}
