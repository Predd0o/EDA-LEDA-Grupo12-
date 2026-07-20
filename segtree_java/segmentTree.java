
public class segmentTree {

    /** Quantidade de elementos do array original. */
    private final int n;

    /** Soma dos elementos cobertos por cada nó. */
    private final long[] treeSum;

    /** Menor elemento coberto por cada nó. */
    private final long[] treeMin;

    /** Maior elemento coberto por cada nó. */
    private final long[] treeMax;

    /**
     * Valor pendente de atualização em intervalo, ainda não propagado aos filhos de
     * cada nó.
     */
    private final long[] lazy;

    /**
     * Constrói a Segment Tree a partir de um array de inteiros. Complexidade O(n).
     *
     * @param arr array de entrada; seus valores são copiados para a árvore — o
     *            array
     *            original não é modificado
     */
    public segmentTree(int[] arr) {
        this.n = arr.length;
        this.treeMax = new long[4 * n];
        this.treeMin = new long[4 * n];
        this.treeSum = new long[4 * n];
        this.lazy = new long[4 * n];
        build(arr, 1, 0, n - 1);
    }

    /**
     * Constrói recursivamente a subárvore do nó {@code node}, responsável pelo
     * intervalo {@code [start, end]} do array original.
     *
     * @param arr   array de entrada
     * @param node  índice do nó atual nos arrays da árvore
     * @param start início (inclusive) do intervalo coberto por este nó
     * @param end   fim (inclusive) do intervalo coberto por este nó
     */
    private void build(int[] arr, int node, int start, int end) {
        if (start == end) {
            treeSum[node] = arr[start];
            treeMin[node] = arr[start];
            treeMax[node] = arr[start];
            return;
        }
        int mid = (start + end) / 2;
        build(arr, 2 * node, start, mid);
        build(arr, 2 * node + 1, mid + 1, end);
        pull(node);
    }

    /**
     * Recalcula soma/mínimo/máximo de {@code node} a partir dos seus dois filhos.
     * Deve ser chamado sempre que um dos filhos é modificado, para manter os
     * agregados do pai consistentes.
     *
     * @param node índice do nó a ser recalculado
     */
    private void pull(int node) {
        treeSum[node] = treeSum[2 * node] + treeSum[2 * node + 1];
        treeMin[node] = Math.min(treeMin[2 * node], treeMin[2 * node + 1]);
        treeMax[node] = Math.max(treeMax[2 * node], treeMax[2 * node + 1]);
    }

    /**
     * Aplica diretamente ao nó {@code node} o efeito de somar {@code val} a todos
     * os
     * elementos do intervalo {@code [start, end]}, e registra esse valor em
     * {@code lazy[node]} para ser repassado aos filhos mais tarde (lazy
     * propagation),
     * evitando descer a árvore inteira a cada atualização em intervalo.
     *
     * @param node  índice do nó
     * @param start início (inclusive) do intervalo coberto por este nó
     * @param end   fim (inclusive) do intervalo coberto por este nó
     * @param val   valor a ser somado a cada elemento do intervalo
     */
    private void applyLazy(int node, int start, int end, long val) {
        treeSum[node] += val * (end - start + 1);
        treeMin[node] += val;
        treeMax[node] += val;
        lazy[node] += val;
    }

    /**
     * Propaga ("empurra") para os dois filhos de {@code node} qualquer atualização
     * pendente em {@code lazy[node]}, e zera o lazy do próprio nó em seguida. Deve
     * ser
     * chamado antes de descer para os filhos em qualquer operação, garantindo que
     * eles
     * reflitam atualizações ainda não aplicadas antes de serem lidos ou
     * modificados.
     *
     * @param node  índice do nó
     * @param start início (inclusive) do intervalo coberto por este nó
     * @param end   fim (inclusive) do intervalo coberto por este nó
     */
    private void push(int node, int start, int end) {
        if (lazy[node] != 0) {
            int mid = (start + end) / 2;
            applyLazy(2 * node, start, mid, lazy[node]);
            applyLazy(2 * node + 1, mid + 1, end, lazy[node]);
            lazy[node] = 0;
        }
    }

    /**
     * Define o valor do elemento de índice {@code idx} como {@code val}.
     * Complexidade
     * O(log n).
     *
     * @param idx índice (0-based) do elemento a ser atualizado
     * @param val novo valor do elemento
     * @throws IndexOutOfBoundsException se {@code idx} estiver fora de
     *                                   {@code [0, n-1]}
     */
    public void updatePoint(int idx, long val) {
        validateIndex(idx);
        updatePoint(1, 0, n - 1, idx, val);
    }

    /**
     * Implementação recursiva de {@link #updatePoint(int, long)}.
     *
     * @param node  índice do nó atual
     * @param start início (inclusive) do intervalo coberto por este nó
     * @param end   fim (inclusive) do intervalo coberto por este nó
     * @param idx   índice do elemento a ser atualizado
     * @param val   novo valor do elemento
     */
    private void updatePoint(int node, int start, int end, int idx, long val) {
        if (start == end) {
            treeSum[node] = val;
            treeMin[node] = val;
            treeMax[node] = val;
            return;
        }
        push(node, start, end);
        int mid = (start + end) / 2;
        if (idx <= mid) {
            updatePoint(2 * node, start, mid, idx, val);
        } else {
            updatePoint(2 * node + 1, mid + 1, end, idx, val);
        }
        pull(node);
    }

    /**
     * Soma {@code val} a cada elemento do intervalo {@code [l, r]}. Complexidade
     * O(log n) graças à lazy propagation — o valor só é de fato propagado às
     * sub-árvores quando alguma outra operação precisar descer até elas.
     *
     * @param l   início (inclusive) do intervalo, 0-based
     * @param r   fim (inclusive) do intervalo, 0-based
     * @param val valor a ser somado a cada elemento de {@code [l, r]}
     * @throws IllegalArgumentException se o intervalo {@code [l, r]} for inválido
     */
    public void updateRange(int l, int r, long val) {
        validateRange(l, r);
        updateRange(1, 0, n - 1, l, r, val);
    }

    /**
     * Implementação recursiva de {@link #updateRange(int, int, long)}.
     *
     * @param node  índice do nó atual
     * @param start início (inclusive) do intervalo coberto por este nó
     * @param end   fim (inclusive) do intervalo coberto por este nó
     * @param l     início (inclusive) do intervalo a ser atualizado
     * @param r     fim (inclusive) do intervalo a ser atualizado
     * @param val   valor a ser somado a cada elemento de {@code [l, r]}
     */
    private void updateRange(int node, int start, int end, int l, int r, long val) {
        if (r < start || end < l)
            return;
        if (l <= start && end <= r) {
            applyLazy(node, start, end, val);
            return;
        }
        push(node, start, end);
        int mid = (start + end) / 2;
        updateRange(2 * node, start, mid, l, r, val);
        updateRange(2 * node + 1, mid + 1, end, l, r, val);
        pull(node);
    }

    /**
     * Retorna a soma dos elementos no intervalo {@code [l, r]}. Complexidade O(log
     * n).
     *
     * @param l início (inclusive) do intervalo, 0-based
     * @param r fim (inclusive) do intervalo, 0-based
     * @return soma dos elementos de {@code [l, r]}
     * @throws IllegalArgumentException se o intervalo {@code [l, r]} for inválido
     */
    public long querySum(int l, int r) {
        validateRange(l, r);
        return querySum(1, 0, n - 1, l, r);
    }

    /**
     * Implementação recursiva de {@link #querySum(int, int)}.
     *
     * @param node  índice do nó atual
     * @param start início (inclusive) do intervalo coberto por este nó
     * @param end   fim (inclusive) do intervalo coberto por este nó
     * @param l     início (inclusive) do intervalo consultado
     * @param r     fim (inclusive) do intervalo consultado
     * @return soma dos elementos de {@code [l, r]} dentro da subárvore de
     *         {@code node}
     */
    private long querySum(int node, int start, int end, int l, int r) {
        if (r < start || end < l)
            return 0;
        if (l <= start && end <= r)
            return treeSum[node];
        push(node, start, end);
        int mid = (start + end) / 2;
        return querySum(2 * node, start, mid, l, r) + querySum(2 * node + 1, mid + 1, end, l, r);
    }

    /**
     * Retorna o menor elemento no intervalo {@code [l, r]}. Complexidade O(log n).
     *
     * @param l início (inclusive) do intervalo, 0-based
     * @param r fim (inclusive) do intervalo, 0-based
     * @return menor valor entre os elementos de {@code [l, r]}
     * @throws IllegalArgumentException se o intervalo {@code [l, r]} for inválido
     */
    public long queryMin(int l, int r) {
        validateRange(l, r);
        return queryMin(1, 0, n - 1, l, r);
    }

    /**
     * Implementação recursiva de {@link #queryMin(int, int)}.
     *
     * @param node  índice do nó atual
     * @param start início (inclusive) do intervalo coberto por este nó
     * @param end   fim (inclusive) do intervalo coberto por este nó
     * @param l     início (inclusive) do intervalo consultado
     * @param r     fim (inclusive) do intervalo consultado
     * @return menor valor entre os elementos de {@code [l, r]} dentro da subárvore
     *         de {@code node}
     */
    private long queryMin(int node, int start, int end, int l, int r) {
        if (r < start || end < l)
            return Long.MAX_VALUE;
        if (l <= start && end <= r)
            return treeMin[node];
        push(node, start, end);
        int mid = (start + end) / 2;
        return Math.min(queryMin(2 * node, start, mid, l, r), queryMin(2 * node + 1, mid + 1, end, l, r));
    }

    /**
     * Retorna o maior elemento no intervalo {@code [l, r]}. Complexidade O(log n).
     *
     * @param l início (inclusive) do intervalo, 0-based
     * @param r fim (inclusive) do intervalo, 0-based
     * @return maior valor entre os elementos de {@code [l, r]}
     * @throws IllegalArgumentException se o intervalo {@code [l, r]} for inválido
     */
    public long queryMax(int l, int r) {
        validateRange(l, r);
        return queryMax(1, 0, n - 1, l, r);
    }

    /**
     * Implementação recursiva de {@link #queryMax(int, int)}.
     *
     * @param node  índice do nó atual
     * @param start início (inclusive) do intervalo coberto por este nó
     * @param end   fim (inclusive) do intervalo coberto por este nó
     * @param l     início (inclusive) do intervalo consultado
     * @param r     fim (inclusive) do intervalo consultado
     * @return maior valor entre os elementos de {@code [l, r]} dentro da subárvore
     *         de {@code node}
     */
    private long queryMax(int node, int start, int end, int l, int r) {
        if (r < start || end < l)
            return Long.MIN_VALUE;
        if (l <= start && end <= r)
            return treeMax[node];
        push(node, start, end);
        int mid = (start + end) / 2;
        return Math.max(queryMax(2 * node, start, mid, l, r), queryMax(node * 2 + 1, mid + 1, end, l, r));
    }

    /**
     * Retorna o valor atual do elemento de índice {@code idx}. Implementado como
     * caso
     * particular de {@link #querySum(int, int)} com {@code l = r = idx}, já que a
     * soma
     * de um único elemento é o próprio elemento. Complexidade O(log n).
     *
     * @param idx índice (0-based) do elemento
     * @return valor atual do elemento em {@code idx}
     * @throws IndexOutOfBoundsException se {@code idx} estiver fora de
     *                                   {@code [0, n-1]}
     */
    public long queryPoint(int idx) {
        validateIndex(idx);
        return querySum(idx, idx);
    }

    /**
     * Valida que {@code idx} é um índice válido do array, ou seja, está em
     * {@code [0, n-1]}.
     *
     * @param idx índice a ser validado
     * @throws IndexOutOfBoundsException se {@code idx} estiver fora de
     *                                   {@code [0, n-1]}
     */
    private void validateIndex(int idx) {
        if (idx < 0 || idx >= n) {
            throw new IndexOutOfBoundsException("Índice fora do intervalo: " + idx);
        }
    }

    /**
     * Valida que {@code [l, r]} é um intervalo válido: ambos os extremos dentro de
     * {@code [0, n-1]} e {@code l <= r}.
     *
     * @param l início do intervalo
     * @param r fim do intervalo
     * @throws IllegalArgumentException se o intervalo for inválido
     */
    private void validateRange(int l, int r) {
        if (l < 0 || r >= n || l > r) {
            throw new IllegalArgumentException("Intervalo inválido: [" + l + ", " + r + "]");
        }
    }

}
