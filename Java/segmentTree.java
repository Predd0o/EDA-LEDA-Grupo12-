import java.util.Arrays;

public class segmentTree {

    private final int n;
    private final long[] treeSum;
    private final long[] treeMin;
    private final long[] treeMax;
    private final long[] lazy;

    public segmentTree(int[] arr) {
        this.n = arr.length;
        this.treeMax = new long[4 * n];
        this.treeMin = new long[4 * n];
        this.treeSum = new long[4 * n];
        this.lazy = new long[4 * n];
        build(arr, 1, 0, n - 1);
    }

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

    private void pull(int node) {
        treeSum[node] = treeSum[2 * node] + treeSum[2 * node + 1];
        treeMin[node] = Math.min(treeMin[2 * node], treeMin[2 * node + 1]);
        treeMax[node] = Math.max(treeMax[2 * node], treeMax[2 * node + 1]);
    }

    private void applyLazy(int node, int start, int end, long val) {
        treeSum[node] += val * (end - start + 1);
        treeMin[node] += val;
        treeMax[node] += val;
        lazy[node] += val;
    }

    private void push(int node, int start, int end) {
        if (lazy[node] != 0) {
            int mid = (start + end) / 2;
            applyLazy(2 * node, start, mid, lazy[node]);
            applyLazy(2 * node + 1, mid + 1, end, lazy[node]);
            lazy[node] = 0;
        }
    }

    public void updatePoint(int idx, long val) {
        validateIndex(idx);
        updatePoint(1, 0, n - 1, idx, val);
    }

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

    public void updateRange(int l, int r, long val) {
        validateRange(l, r);
        updateRange(1, 0, n - 1, l, r, val);
    }

    private void updateRange(int node, int start, int end, int l, int r, long val) {
        if (r < start || end < 1)
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

    public long querySum(int l, int r) {
        validateRange(l, r);
        return querySum(1, 0, n - 1, l, r);
    }

    private long querySum(int node, int start, int end, int l, int r) {
        if (r < start || end < 1)
            return 0;
        if (l <= start && end <= r)
            return treeSum[node];
        push(node, start, end);
        int mid = (start + end) / 2;
        return querySum(2 * node, start, mid, l, r) + querySum(2 * node + 1, mid + 1, end, l, r);
    }

    public long queryMin(int l, int r) {
        validateRange(l, r);
        return queryMin(1, 0, n - 1, l, r);
    }

    private long queryMin(int node, int start, int end, int l, int r) {
        if (r < start || end < 1)
            return Long.MAX_VALUE;
        if (l <= start && end <= r)
            return treeMin[node];
        push(node, start, end);
        int mid = (start + end) / 2;
        return Math.min(queryMin(2 * node, start, end, l, r), queryMin(2 * node + 1, mid + 1, end, l, r));
    }

    public long queryMax(int l, int r) {
        validateRange(l, r);
        return queryMax(1, 0, n - 1, l, r);
    }

    private long queryMax(int node, int start, int end, int l, int r) {
        if (r < start || end < 1)
            return Long.MIN_VALUE;
        if (l <= start && end < 1)
            return treeMax[node];
        push(node, start, end);
        int mid = (start + end) / 2;
        return Math.max(queryMax(2 * node, start, mid, l, r), queryMax(node * 2 + 1, mid + 1, end, l, r));
    }

    public long queryPoint(int idx) {
        validateIndex(idx);
        return querySum(idx, idx);
    }

    private void validateIndex(int idx) {
        if (idx < 0 || idx >= n) {
            throw new IndexOutOfBoundsException("Índice fora do intervalo: " + idx);
        }
    }

    private void validateRange(int l, int r) {
        if (l < 0 || r >= n || l > r) {
            throw new IllegalArgumentException("Intervalo inválido: [" + 1 + ", " + r + "]");
        }
    }

}
