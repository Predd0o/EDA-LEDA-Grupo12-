import math

class SegmentTree:

    # Construtor que recebe como parâmetro um array de inteiros. O(n)
    def __init__(self, arr):
        self.n = len(arr)
        self.tree_max = [0] * (4 * self.n)
        self.tree_min = [0] * (4 * self.n)
        self.tree_sum = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self.build(arr, 1, 0, self.n - 1)

    # Método que constrói recursivamente a árvore
    def _build(self, arr, node, start, end):
        if start == end:
            self.tree_sum[node] = arr[start]
            self.tree_min[node] = arr[start]
            self.tree_max[node] = arr[start]
            return

        mid = (start + end) // 2
        self.build(arr, 2*node, start, mid)
        self.build(arr, 2*node + 1, mid + 1, end)
        self.pull(node)

    # Método responsável por recalcular o valor (soma/mínimo/máximo) de um nó a partir
    # dos valores de seus filhos. Deve ser invocado toda vez que um dos filhos é
    # modificado.
    def _pull(self, node):
        self.tree_sum[node] = self.tree_sum[2*node] + self.tree_sum[2*node + 1]
        self.tree_min[node] = math.min(self.tree_min[2*node], self.tree_min[2*node + 1])
        self.tree_max[node] = math.max(self.tree_max[2*node], self.tree_max[2*node + 1])

    # Aplica o valor a ser propagado, em um intervalo específico, diretamente no nó e
    # regista esse valor a ser adicionado no array "lazy" para ser repassado aos filhos
    # em uma futura descida pela árvore
    def  _apply_lazy(self, node, start, end, val):
        self.tree_sum[node] += val * (end - start + 1)
        self.tree_min[node] += val
        self.tree_max[node] += val
        self.lazy[node] += val

    # Propaga ("empurra") para os dois filhos do nó qualquer atualização pendente no 
    # array "lazy" e, em seguida, zera o lazy do próprio nó. Esse método deve ser
    # chamado antes de descer para os filhos em qualquer operação, garantindo a correta
    # atualização de seus valores.
    def _push(self, node, start, end):
        if self.lazy[node] != 0:
            mid = (start + end) // 2
            self._apply_lazy(2*node, start, mid, self.lazy[node])
            self._apply_lazy(2*node + 1, mid + 1, end, self.lazy[node])
            self.lazy[node] = 0;

    # Define o valor de um elemento de índice "idx" para o valor passado em "val"
    # Complexidade O(log n)
    def update_point(self, idx, val):
        self.validate_index(idx)
        self.update_point(1, 0, self.n - 1, idx, val)

    # Implementação recursiva do método de Atualização de um nó único
    def _update_point(self, node, start, end, idx, val):
        if start == end:
            self.tree_sum[node] = val
            self.tree_min[node] = val
            self.tree_max[node] = val
            return

        self._push(node, start, end)
        mid = (start + end) // 2
        if idx <= mid:
            self._update_point(2*node, start, mid, idx, val)
        else:
            self._update_point(2*node + 1, mid + 1, end, idx, val)
        self._pull(node)

    # Método responsável por somar o valor "val" a cada elemento do intervalo [l,r]
    # Graças à Lazy Propagation, o valor só é de fato propagado às sub-árvores quando
    # alguma outra operação precisar passar por elas
    # Complexidade O(log n)
    def update_range(self, l, r, val):
        self.validate_range(l, r)
        self._update_range(1, 0, self.n - 1, l, r, val)

    # Implementação recursiva do método "update_range"
    def _update_range(self, node, start, end, l, r, val):
        if r < start or end < l: # nó com intervalo totalmente fora de [l,r]
            return

        if l <= start and end <= r: # nó com intervalo totalmente dentr de [l,r]
            self._apply_lazy(node, start, end, val)
            return

        # caso o nó tenha um intervalo parcialmente contido em [l,r] deve-se continuar a
        # recursão
        self._push(node, start, end) # garantindo a lazy propagation
        mid = (start + end) // 2
        self._update_range(2*node, start, mid, l, r, val)
        self._update_range(2*node + 1, mid + 1, end, l, r, val)
        self._pull(node) # "puxando" os novos valores dos filhos para atualizar "node"

    # Método que retorna a soma dos elementos no intervalo [l,r]. O(log n)
    def query_sum(self, l, r):
        self.validate_range(l, r)
        return self._query_sum(1, 0, self.n - 1, l, r)

    # Implementação recursiva do método "query_sum"
    def _query_sum(self, node, start, end, l, r):
        if r < start or end < l:
            return 0

        if l <= start and end <= r:
            return self.tree_sum[node]

        self._push(node, start, end)
        mid = (start + end) // 2
        return self._query_sum(2*node, start, mid, l, r) + self._query_sum(2*node + 1, mid + 1, end, l, r)
    

    # Método que retorna o menor elemento no intervalo [l,r]. O(log n)
    def query_min(self, l, r):
        self.validate_range(l, r)
        return self._query_min(1, 0, self.n - 1, l, r)

    # Implementação recursiva do método "query_min"
    def _query_min(self, node, start, end, l, r):
        if r < start or end < l:
            return float("inf")

        if l <= start and end <= r:
            return self.tree_min[node]

        self._push(node, start, end)
        mid = (start + end) // 2
        return math.min(self._query_min(2*node, start, mid, l, r), self._query_min(2*node + 1, mid + 1, end, l, r))

    # Método que retorna o maior elemento no intervalo [l,r]. O(log n)
    def query_max(self, l, r):
        self.validate_range(l, r)
        return self._query_max(1, 0, self.n - 1, l, r)

    # Implementação recursiva do método "query_max"
    def _query_max(self, node, start, end, l, r):
        if r < start or end < l:
            return float("-inf")

        if l <= start and end <= r:
            return self.tree_max[node]

        self._push(node, start, end)
        mid = (start + end) // 2
        return math.max(self._query_max(2*node, start, mid, l, r), self._query_max(2*node + 1, mid + 1, end, l, r))
    
    # Método responsável por retornar o valor de determinado elemento no índice "idx"
    # Implementado como caso particular de uma consulta de intervalo, na qual o intervalo
    # analisado é um com l = r = idx. O(log n)
    def query_point(self, idx):
        self.validate_index(idx)
        return self.query_sum(idx, idx)

    # Método para validar que "idx" é um índice válido no array
    def validate_index(self, idx):
        if idx < 0 or idx >= self.n:
            raise IndexError("Índice fora do intervalo: " + idx)

    # Método para validar que "[l,r]" é um intervalo válido
    def validate_range(self, l, r):
        if l < 0 or r >= self.n or l > r:
            raise ValueError("Intervalo inválido: [" + l + ", " + r + "]")


    



