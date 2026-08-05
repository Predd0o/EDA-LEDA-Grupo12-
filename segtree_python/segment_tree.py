class SegmentTree:
    """
    Implementação de uma Árvore de Segmentos (Segment Tree) com Lazy Propagation.

    Essa estrutura permite realizar as operações de consulta (soma/mínimo/máximo) e 
    de atualização, tanto em pontos específicos quanto em intervalos.

    Attributes:
        tree_max (list): o array que armazena os nós da Segment Tree de Máximo.
        tree_min (list): o array que armazena os nós da Segment Tree de Mínimo.
        tree_sum (list): o array que armazena os nós da Segment Tree de Soma.
        lazy (list): array utilizado para armazenar atualizações pendentes nos
                     valores dos nós, seguindo o mecanismo de Lazy Propagation.
        nodes_visited (int): o contador para o número de nós visitados durante
                    alguma operação na árvore.
        n (int): o tamanho do array original.
    """

    def __init__(self, arr):
        """
        Inicializa as Segment Trees com base no array passado como parâmetro. O
        tamanho inicial delas será o tamanho do array original multiplicado por 4.

        Args:
            arr (list): o array original com os valores de origem para a Segment Tree.
        """
        self.n = len(arr)
        self.tree_max = [0] * (4 * self.n)
        self.tree_min = [0] * (4 * self.n)
        self.tree_sum = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self.nodes_visited = 0
        self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        """
        Método que constrói recursivamente a árvore.
        
        Complexidade: O(n)

        Args:
            arr (list): o array original com os valores.
            node (int): o índice do nó atual na árvore.
            start (int): o limite inicial do intervalo representado pelo nó.
            end (int): o limite final do intervalo representado pelo nó.
        """
        self.nodes_visited += 1 # toda chamada de método recursivo é um acesso a nó
        # por isso, todo início desse tipo de método possuirá essa incrementação 

        if start == end:
            self.tree_sum[node] = arr[start]
            self.tree_min[node] = arr[start]
            self.tree_max[node] = arr[start]
            return

        mid = (start + end) // 2
        self._build(arr, 2*node, start, mid)
        self._build(arr, 2*node + 1, mid + 1, end)
        self._pull(node)

    def _pull(self, node):
        """
        Método responsável por recalcular o valor (soma/mínimo/máximo) de um nó a partir
        dos valores de seus filhos. Deve ser invocado toda vez que um dos filhos é
        modificado.

        Complexidade: O(1)

        Args:
            node (int): o índice do nó a ser recalculado.
        """
        self.tree_sum[node] = self.tree_sum[2*node] + self.tree_sum[2*node + 1]
        self.tree_min[node] = min(self.tree_min[2*node], self.tree_min[2*node + 1])
        self.tree_max[node] = max(self.tree_max[2*node], self.tree_max[2*node + 1])

    def _apply_lazy(self, node, start, end, val):
        """
        Aplica o valor a ser propagado, em um intervalo específico, diretamente no nó e
        registra esse valor a ser adicionado no array "lazy" para ser repassado aos filhos
        em uma futura descida pela árvore.

        Complexidade: O(1)

        Args:
            node (int): o índice do nó onde o valor será aplicado.
            start (int): o limite inicial do intervalo do nó.
            end (int): o limite final do intervalo do nó.
            val (int): o valor a ser adicionado ao nó.
        """
        self.tree_sum[node] += val * (end - start + 1)
        self.tree_min[node] += val
        self.tree_max[node] += val
        self.lazy[node] += val

    def _push(self, node, start, end):
        """
        Propaga ("empurra") para os dois filhos do nó qualquer atualização pendente no 
        array "lazy" e, em seguida, zera o lazy do próprio nó. Esse método deve ser
        chamado antes de descer para os filhos em qualquer operação, garantindo a correta
        atualização de seus valores.

        Complexidade: O(1)

        Args:
            node (int): o índice do nó cujas atualizações pendentes serão propagadas.
            start (int): o limite inicial do intervalo do nó.
            end (int): o limite final do intervalo do nó.
        """
        if self.lazy[node] != 0:
            mid = (start + end) // 2
            self._apply_lazy(2*node, start, mid, self.lazy[node])
            self._apply_lazy(2*node + 1, mid + 1, end, self.lazy[node])
            self.lazy[node] = 0

    def update_point(self, idx, val):
        """
        Define o valor de um elemento de índice "idx" para o valor passado em "val".

        Args:
            idx (int): o índice do elemento a ser atualizado.
            val (int): o novo valor a ser definido.
        """
        self.validate_index(idx)
        self._update_point(1, 0, self.n - 1, idx, val)

    def _update_point(self, node, start, end, idx, val):
        """
        Implementação recursiva do método de Atualização de um nó único.

        Complexidade: O(log n)

        Args:
            node (int): o índice do nó atual na árvore.
            start (int): o limite inicial do intervalo do nó.
            end (int): o limite final do intervalo do nó.
            idx (int): o índice do elemento original que está sendo atualizado.
            val (int): o novo valor a ser definido.
        """
        self.nodes_visited += 1

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

    def update_range(self, l, r, val):
        """
        Método responsável por somar o valor "val" a cada elemento do intervalo [l,r].
        Graças à Lazy Propagation, o valor só é, de fato, propagado às sub-árvores quando
        alguma outra operação precisar passar por elas.

        Args:
            l (int): o limite inicial do intervalo a ser atualizado.
            r (int): o limite final do intervalo a ser atualizado.
            val (int): o valor a ser somado a cada elemento do intervalo.
        """
        self.validate_range(l, r)
        self._update_range(1, 0, self.n - 1, l, r, val)

    def _update_range(self, node, start, end, l, r, val):
        """
        Implementação recursiva do método "update_range".

        Complexidade: O(log n)

        Args:
            node (int): o índice do nó atual.
            start (int): o limite inicial do intervalo do nó.
            end (int): o limite final do intervalo do nó.
            l (int): o limite inicial do intervalo a ser atualizado.
            r (int): o limite final do intervalo a ser atualizado.
            val (int): o valor a ser somado.
        """
        self.nodes_visited += 1

        # nó com intervalo totalmente fora de [l,r]
        if r < start or end < l: 
            return

        # nó com intervalo totalmente dentro de [l,r]
        if l <= start and end <= r: 
            self._apply_lazy(node, start, end, val)
            return

        # caso o nó tenha um intervalo parcialmente contido em [l,r] deve-se continuar a 
        # recursão
        self._push(node, start, end) # garantindo a lazy propagation
        mid = (start + end) // 2
        self._update_range(2*node, start, mid, l, r, val)
        self._update_range(2*node + 1, mid + 1, end, l, r, val)
        self._pull(node) # "puxando" os novos valores dos filhos para atualizar "node"

    def query_sum(self, l, r):
        """
        Método que retorna a soma dos elementos no intervalo [l,r]. 

        Args:
            l (int): o limite inicial do intervalo a ser consultado.
            r (int): o limite final do intervalo a ser consultado.

        Returns:
            int: a soma dos elementos no intervalo especificado.
        """
        self.validate_range(l, r)
        return self._query_sum(1, 0, self.n - 1, l, r)

    def _query_sum(self, node, start, end, l, r):
        """
        Implementação recursiva do método "query_sum".

        Complexidade: O(log n)

        Args:
            node (int): o índice do nó atual.
            start (int): o limite inicial do intervalo do nó.
            end (int): o limite final do intervalo do nó.
            l (int): o limite inicial do intervalo da consulta.
            r (int): o limite final do intervalo da consulta.

        Returns:
            int: a soma no intervalo analisado, ou 0 se estiver fora dos limites.
        """
        self.nodes_visited += 1

        if r < start or end < l:
            return 0

        if l <= start and end <= r:
            return self.tree_sum[node]

        self._push(node, start, end)
        mid = (start + end) // 2
        return self._query_sum(2*node, start, mid, l, r) + self._query_sum(2*node + 1, mid + 1, end, l, r)
    
    def query_min(self, l, r):
        """
        Método que retorna o menor elemento no intervalo [l,r]. 

        Args:
            l (int): o limite inicial do intervalo a ser consultado.
            r (int): o limite final do intervalo a ser consultado.

        Returns:
            int: o valor mínimo no intervalo especificado.
        """
        self.validate_range(l, r)
        return self._query_min(1, 0, self.n - 1, l, r)

    def _query_min(self, node, start, end, l, r):
        """
        Implementação recursiva do método "query_min".

        Complexidade: O(log n)

        Args:
            node (int): o índice do nó atual.
            start (int): o limite inicial do intervalo do nó.
            end (int): o limite final do intervalo do nó.
            l (int): o limite inicial do intervalo da consulta.
            r (int): o limite final do intervalo da consulta.

        Returns:
            float|int: o valor mínimo no intervalo analisado, ou infinito positivo se o 
            intervalo do nó estiver fora dos limites de [l,r] (para não atrapalhar o cálculo
            do mínimo).
        """
        self.nodes_visited += 1

        if r < start or end < l:
            return float("inf")

        if l <= start and end <= r:
            return self.tree_min[node]

        self._push(node, start, end)
        mid = (start + end) // 2
        return min(self._query_min(2*node, start, mid, l, r), self._query_min(2*node + 1, mid + 1, end, l, r))

    def query_max(self, l, r):
        """
        Método que retorna o maior elemento no intervalo [l,r]. 
        
        Complexidade: O(log n)

        Args:
            l (int): o limite inicial do intervalo a ser consultado.
            r (int): o limite final do intervalo a ser consultado.

        Returns:
            int: o valor máximo no intervalo especificado.
        """
        self.validate_range(l, r)
        return self._query_max(1, 0, self.n - 1, l, r)

    def _query_max(self, node, start, end, l, r):
        """
        Implementação recursiva do método "query_max".

        Complexidade: O(log n)

        Args:
            node (int): o índice do nó atual.
            start (int): o limite inicial do intervalo do nó.
            end (int): o limite final do intervalo do nó.
            l (int): o limite inicial do intervalo da consulta.
            r (int): o limite final do intervalo da consulta.

        Returns:
            float|int: o valor máximo no intervalo analisado, ou infinito negativo se o
            intervalo do nó estiver fora dos limites de [l,r] (para não atrapalhar o
            cálculo do máximo).
        """
        self.nodes_visited += 1

        if r < start or end < l:
            return float("-inf")

        if l <= start and end <= r:
            return self.tree_max[node]

        self._push(node, start, end)
        mid = (start + end) // 2
        return max(self._query_max(2*node, start, mid, l, r), self._query_max(2*node + 1, mid + 1, end, l, r))
    
    def query_point(self, idx):
        """
        Método responsável por retornar o valor de determinado elemento no índice "idx".
        Implementado como caso particular de uma consulta de intervalo, na qual o intervalo
        analisado é um com l = r = idx.
        
        Complexidade: O(log n)

        Args:
            idx (int): o índice do elemento a ser consultado.

        Returns:
            int: o valor do elemento na posição 'idx'.
        """
        self.validate_index(idx)
        return self.query_sum(idx, idx)

    def validate_index(self, idx):
        """
        Método para validar que "idx" é um índice válido no array.

        Args:
            idx (int): o índice a ser testado.
            
        Raises:
            IndexError: Se o índice estiver fora dos limites do array original.
        """
        if idx < 0 or idx >= self.n:
            raise IndexError("Índice fora do intervalo: " + str(idx))

    def validate_range(self, l, r):
        """
        Método para validar que "[l,r]" é um intervalo válido.

        Args:
            l (int): o início do intervalo.
            r (int): o final do intervalo.
            
        Raises:
            ValueError: Se o intervalo for inválido.
        """
        if l < 0 or r >= self.n or l > r:
            raise ValueError("Intervalo inválido: [" + str(l) + ", " + str(r) + "]")

    def reset_counter(self):
        """
        Método responsável por zerar o contador "nodes_visited" ao final de cada
        operação de update (atualização) ou de query (consulta).
        """
        self.nodes_visited = 0

    def get_counter(self):
        """
        Método responsável por devolver o número de nós visitados, contido no contador.
        """
        return self.nodes_visited