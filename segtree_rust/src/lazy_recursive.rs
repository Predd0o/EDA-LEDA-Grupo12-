//! Implementação de Segment Tree com lazy propagation recursiva.
//! Suporta queries de soma, mínimo e máximo, e atualizações de intervalo e ponto.

use std::cmp::{max, min};

/// Contadores de instrumentação de nós visitados na árvore.
#[derive(Debug, Clone)]
pub struct Counters {
    pub nodes_visited: u64,
}

impl Counters {
    fn new() -> Self {
        Counters { nodes_visited: 0 }
    }

    fn reset(&mut self) {
        self.nodes_visited = 0;
    }
}

/// Árvore de segmentos com propagação preguiçosa (lazy propagation).
///
/// Suporta queries de soma, mínimo e máximo, e atualizações de intervalo e ponto.
pub struct SegmentTree {
    n: usize,
    sum_tree: Vec<i64>,
    min_tree: Vec<i64>,
    max_tree: Vec<i64>,
    lazy: Vec<i64>,
    counters: Counters,
}

impl SegmentTree {
    /// Constrói a SegmentTree a partir do array fornecido.
    ///
    /// # Arguments
    /// * `arr` - Array de entrada de valores `i64`.
    ///
    /// # Returns
    /// Uma instância de `SegmentTree` construída.
    ///
    /// # Complexity
    /// O(n)
    pub fn build(arr: &[i64]) -> Self {
        let n = arr.len();
        let size = 4 * n;
        let mut st = SegmentTree {
            n,
            sum_tree: vec![0; size],
            min_tree: vec![0; size],
            max_tree: vec![0; size],
            lazy: vec![0; size],
            counters: Counters::new(),
        };
        if n > 0 {
            st.build_helper(1, 0, n - 1, arr);
        }
        st
    }

    pub fn reset_counters(&mut self) {
        self.counters.reset();
    }

    pub fn counters(&self) -> &Counters {
        &self.counters
    }

    fn build_helper(&mut self, node: usize, i: usize, j: usize, arr: &[i64]) {
        self.counters.nodes_visited += 1;
        if i == j {
            self.sum_tree[node] = arr[i];
            self.min_tree[node] = arr[i];
            self.max_tree[node] = arr[i];
            return;
        }
        let mid = (i + j) / 2;
        let left_child = 2 * node;
        let right_child = 2 * node + 1;
        self.build_helper(left_child, i, mid, arr);
        self.build_helper(right_child, mid + 1, j, arr);
        self.pull(node);
    }

    fn pull(&mut self, node: usize) {
        let left_child = 2 * node;
        let right_child = 2 * node + 1;
        let left_sum = self.sum_tree[left_child];
        let right_sum = self.sum_tree[right_child];
        self.sum_tree[node] = left_sum + right_sum;

        let left_min = self.min_tree[left_child];
        let right_min = self.min_tree[right_child];
        self.min_tree[node] = min(left_min, right_min);

        let left_max = self.max_tree[left_child];
        let right_max = self.max_tree[right_child];
        self.max_tree[node] = max(left_max, right_max);
    }

    fn push(&mut self, node: usize, i: usize, j: usize) {
        if self.lazy[node] != 0 {
            let mid = (i + j) / 2;
            self.apply_lazy(2 * node, i, mid, self.lazy[node]);
            self.apply_lazy(2 * node + 1, mid + 1, j, self.lazy[node]);
            self.lazy[node] = 0;
        }
    }

    fn apply_lazy(&mut self, node: usize, start: usize, end: usize, value: i64) {
        let range_size = (end - start + 1) as i64;
        self.sum_tree[node] += value * range_size;
        self.min_tree[node] += value;
        self.max_tree[node] += value;
        self.lazy[node] += value;
    }

    /// Adiciona `value` a todos os elementos no intervalo `[left, right]`.
    ///
    /// # Arguments
    /// * `left` - Índice inicial do intervalo (inclusive).
    /// * `right` - Índice final do intervalo (inclusive).
    /// * `value` - Valor a ser adicionado a cada elemento do intervalo.
    ///
    /// # Complexity
    /// O(log n)
    pub fn update_range(&mut self, left: usize, right: usize, value: i64) {
        if self.n == 0 {
            return;
        }
        self.update_range_helper(1, 0, self.n - 1, left, right, value);
    }

    fn update_range_helper(
        &mut self,
        node: usize,
        i: usize,
        j: usize,
        left: usize,
        right: usize,
        value: i64,
    ) {
        self.counters.nodes_visited += 1;
        if right < i || j < left {
            return;
        }
        if left <= i && j <= right {
            self.apply_lazy(node, i, j, value);
            return;
        }
        self.push(node, i, j);
        let mid = (i + j) / 2;
        self.update_range_helper(2 * node, i, mid, left, right, value);
        self.update_range_helper(2 * node + 1, mid + 1, j, left, right, value);
        self.pull(node);
    }

    /// Define o valor do elemento no índice `index` para `value`.
    ///
    /// # Arguments
    /// * `index` - Índice do elemento a atualizar.
    /// * `value` - Novo valor do elemento.
    ///
    /// # Complexity
    /// O(log n)
    pub fn update_point(&mut self, index: usize, value: i64) {
        if self.n == 0 {
            return;
        }
        self.update_point_helper(1, 0, self.n - 1, index, value);
    }

    fn update_point_helper(
        &mut self,
        node: usize,
        i: usize,
        j: usize,
        index: usize,
        value: i64,
    ) {
        self.counters.nodes_visited += 1;
        if i == j {
            self.sum_tree[node] = value;
            self.min_tree[node] = value;
            self.max_tree[node] = value;
            return;
        }
        self.push(node, i, j);
        let mid = (i + j) / 2;
        if index <= mid {
            self.update_point_helper(2 * node, i, mid, index, value);
        } else {
            self.update_point_helper(2 * node + 1, mid + 1, j, index, value);
        }
        self.pull(node);
    }

    /// Retorna a soma dos elementos no intervalo `[left, right]`.
    ///
    /// # Arguments
    /// * `left` - Índice inicial do intervalo (inclusive).
    /// * `right` - Índice final do intervalo (inclusive).
    ///
    /// # Returns
    /// Soma dos elementos no intervalo.
    ///
    /// # Complexity
    /// O(log n)
    pub fn query_sum(&mut self, left: usize, right: usize) -> i64 {
        if self.n == 0 || right < left {
            return 0;
        }
        self.query_sum_helper(1, 0, self.n - 1, left, right)
    }

    fn query_sum_helper(
        &mut self,
        node: usize,
        i: usize,
        j: usize,
        left: usize,
        right: usize,
    ) -> i64 {
        self.counters.nodes_visited += 1;
        if right < i || j < left {
            return 0;
        }
        if left <= i && j <= right {
            return self.sum_tree[node];
        }
        self.push(node, i, j);
        let mid = (i + j) / 2;
        let sum_left = self.query_sum_helper(2 * node, i, mid, left, right);
        let sum_right = self.query_sum_helper(2 * node + 1, mid + 1, j, left, right);
        sum_left + sum_right
    }

    /// Retorna o mínimo dos elementos no intervalo `[left, right]`.
    ///
    /// # Arguments
    /// * `left` - Índice inicial do intervalo (inclusive).
    /// * `right` - Índice final do intervalo (inclusive).
    ///
    /// # Returns
    /// Valor mínimo no intervalo.
    ///
    /// # Complexity
    /// O(log n)
    pub fn query_min(&mut self, left: usize, right: usize) -> i64 {
        if self.n == 0 || right < left {
            return i64::MAX;
        }
        self.query_min_helper(1, 0, self.n - 1, left, right)
    }

    fn query_min_helper(
        &mut self,
        node: usize,
        i: usize,
        j: usize,
        left: usize,
        right: usize,
    ) -> i64 {
        self.counters.nodes_visited += 1;
        if right < i || j < left {
            return i64::MAX;
        }
        if left <= i && j <= right {
            return self.min_tree[node];
        }
        self.push(node, i, j);
        let mid = (i + j) / 2;
        let min_left = self.query_min_helper(2 * node, i, mid, left, right);
        let min_right = self.query_min_helper(2 * node + 1, mid + 1, j, left, right);
        min(min_left, min_right)
    }

    /// Retorna o máximo dos elementos no intervalo `[left, right]`.
    ///
    /// # Arguments
    /// * `left` - Índice inicial do intervalo (inclusive).
    /// * `right` - Índice final do intervalo (inclusive).
    ///
    /// # Returns
    /// Valor máximo no intervalo.
    ///
    /// # Complexity
    /// O(log n)
    pub fn query_max(&mut self, left: usize, right: usize) -> i64 {
        if self.n == 0 || right < left {
            return i64::MIN;
        }
        self.query_max_helper(1, 0, self.n - 1, left, right)
    }

    fn query_max_helper(
        &mut self,
        node: usize,
        i: usize,
        j: usize,
        left: usize,
        right: usize,
    ) -> i64 {
        self.counters.nodes_visited += 1;
        if right < i || j < left {
            return i64::MIN;
        }
        if left <= i && j <= right {
            return self.max_tree[node];
        }
        self.push(node, i, j);
        let mid = (i + j) / 2;
        let max_left = self.query_max_helper(2 * node, i, mid, left, right);
        let max_right = self.query_max_helper(2 * node + 1, mid + 1, j, left, right);
        max(max_left, max_right)
    }
}

#[cfg(test)]
mod tests {
    use super::SegmentTree;

    #[test]
    fn build_and_query_sum() {
        let arr: Vec<i64> = (0..16).collect();
        let mut st = SegmentTree::build(&arr);
        assert_eq!(st.counters().nodes_visited, 31); // 2*16 - 1 = 31
        st.reset_counters();
        assert_eq!(st.query_sum(0, 15), 120);
        assert_eq!(st.counters().nodes_visited, 1); // Exact root match = 1 node
        assert_eq!(st.query_sum(1, 9), 45);
    }

    #[test]
    fn query_min() {
        let arr: Vec<i64> = (0..10).collect();
        let mut st = SegmentTree::build(&arr);
        assert_eq!(st.query_min(1, 9), 1);
    }

    #[test]
    fn query_max() {
        let arr: Vec<i64> = (0..10).collect();
        let mut st = SegmentTree::build(&arr);
        assert_eq!(st.query_max(1, 9), 9);
    }

    #[test]
    fn range_update_add() {
        let arr: Vec<i64> = (0..10).collect();
        let mut st = SegmentTree::build(&arr);
        st.update_range(0, 9, 20);
        assert_eq!(st.query_sum(0, 1), 41);
        assert_eq!(st.query_sum(0, 9), 45 + 20 * 10);
    }

    #[test]
    fn point_update() {
        let arr: Vec<i64> = (0..10).collect();
        let mut st = SegmentTree::build(&arr);
        st.update_point(5, 100);
        assert_eq!(st.query_sum(5, 5), 100);
        assert_eq!(st.query_min(0, 9), 0);
        assert_eq!(st.query_max(0, 9), 100);
    }

    #[test]
    fn empty_tree() {
        let arr: Vec<i64> = vec![];
        let mut st = SegmentTree::build(&arr);
        assert_eq!(st.query_sum(0, 0), 0);
    }
}
