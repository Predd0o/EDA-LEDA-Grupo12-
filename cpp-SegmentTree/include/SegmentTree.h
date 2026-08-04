#pragma once

#include <vector>
#include <cstdint>

/**
 * @file SegmentTree.h
 * @author Luis Guilherme Brito Ceglia Araújo
 * 
 * @class SegmentTree
 * @brief Implementa uma Segment Tree com Lazy Propagation.
 *
 * Esta classe permite consultas e atualizações eficientes sobre um vetor
 * de valores inteiros utilizando a estrutura de dados Segment Tree.
 *
 * Operações suportadas:
 * - Consulta da soma de um intervalo.
 * - Consulta do menor valor de um intervalo.
 * - Consulta do maior valor de um intervalo.
 * - Atualização de um único elemento.
 * - Atualização de um intervalo inteiro utilizando Lazy Propagation.
 *
 * Complexidades:
 * - Construção: O(n)
 * - Atualização pontual: O(log n)
 * - Atualização em intervalo: O(log n)
 * - Consultas: O(log n)
 *
 * A implementação utiliza quatro vetores internos:
 * - sumTree: armazena a soma de cada segmento.
 * - minTree: armazena o menor elemento de cada segmento.
 * - maxTree: armazena o maior elemento de cada segmento.
 * - lazy: armazena atualizações pendentes para Lazy Propagation.
 */


/**
 * @brief Contador de nós visitados durante uma operação.
 */
struct Counters {

    /**
     * @brief Quantidade de nós visitados.
     */
    uint64_t visitedNodes = 0;
};




 class SegmentTree {



    private:
    
    /**
     * @brief Número de elementos do vetor original.
     */
    int n;

    /**
     * @brief Segment Tree responsável pelas somas.
     */
    std::vector<long long> sumTree;

    /**
     * @brief Segment Tree responsável pelos máximos.
     */
    std::vector<long long> maxTree;

    /**
     * @brief Segment Tree responsável pelos mínimos.
     */
    std::vector<long long> minTree;

    /**
     * @brief Vetor utilizado para Lazy Propagation.
     */
    std::vector<long long> lazy;

    /**
    * @brief Contador de nós visitados durante uma operação.
    */
    Counters counters;


    /**
     * @brief Constrói recursivamente a árvore.
     *
     * @param arr Vetor original.
     * @param node Nó atual da Segment Tree.
     * @param start Início do segmento.
     * @param end Final do segmento.
     */
    void build(const std::vector<long long>& arr, int node, int start, int end);

    /**
     * @brief Atualiza um nó utilizando as informações dos filhos.
     *
     * Recalcula soma, mínimo e máximo após modificações nos filhos.
     *
     * @param node Nó a ser atualizado.
     */
    void pull(int node);

    /**
     * @brief Aplica uma atualização preguiçosa (Lazy Propagation).
     *
     * Atualiza o segmento representado por um nó sem propagar
     * imediatamente a atualização para seus descendentes.
     *
     * @param node Nó atual.
     * @param start Início do segmento.
     * @param end Final do segmento.
     * @param value Valor a ser adicionado.
     */
    void applyLazy(int node, int start, int end, long long value);

    /**
     * @brief Propaga atualizações pendentes para os filhos.
     *
     * @param node Nó atual.
     * @param start Início do segmento.
     * @param end Final do segmento.
     */
    void push(int node, int start, int end);

    /**
     * @brief Atualiza um único elemento da árvore.
     *
     * @param node Nó atual.
     * @param start Início do segmento.
     * @param end Final do segmento.
     * @param index Índice a ser atualizado.
     * @param value Novo valor.
     */
    void updatePoint(int node, int start, int end,
                     int index, long long value);
    
    /**
     * @brief Atualiza todos os elementos de um intervalo.
     *
     * Utiliza Lazy Propagation para manter complexidade O(log n).
     *
     * @param node Nó atual.
     * @param start Início do segmento.
     * @param end Final do segmento.
     * @param left Limite esquerdo.
     * @param right Limite direito.
     * @param value Valor a ser adicionado.
     */
    void updateRange(int node, int start, int end,
                     int left, int right, long long value);
    
    /**
     * @brief Consulta a soma de um intervalo.
     *
     * @return Soma dos elementos do intervalo.
     */
    [[nodiscard]]
    long long querySum(int node, int start, int end,
                       int left, int right);
    
    /**
     * @brief Consulta o menor valor de um intervalo.
     *
     * @return Menor elemento encontrado.
     */
    [[nodiscard]]
    long long queryMin(int node, int start, int end,
                       int left, int right);
    
    /**
     * @brief Consulta o maior valor de um intervalo.
     *
     * @return Maior elemento encontrado.
     */
    [[nodiscard]]
    long long queryMax(int node, int start, int end,
                       int left, int right);
    
    /**
     * @brief Verifica se um índice é válido.
     *
     * @param index Índice a ser validado.
     * @throw std::out_of_range Caso o índice seja inválido.
     */
    void validateIndex(int index);

    /**
     * @brief Verifica se um intervalo é válido.
     *
     * @param left Limite esquerdo.
     * @param right Limite direito.
     * @throw std::out_of_range Caso o intervalo seja inválido.
     */
    void validateRange(int left, int right);

public:
    /**
     * @brief Constrói uma Segment Tree a partir de um vetor.
     *
     * Complexidade: O(n)
     *
     * @param arr Vetor inicial.
     *
     * @throw std::invalid_argument Caso o vetor esteja vazio.
     */
    explicit SegmentTree(const std::vector<long long>& arr);

    /**
     * @brief Atualiza um único elemento.
     *
     * Complexidade: O(log n)
     *
     * @param index Índice do elemento.
     * @param value Novo valor.
     */
    void updatePoint(int index, long long value);
    
    /**
     * @brief Atualiza todos os elementos de um intervalo.
     *
     * Complexidade: O(log n)
     *
     * @param left Limite esquerdo.
     * @param right Limite direito.
     * @param value Valor a ser adicionado.
     */
    void updateRange(int left, int right, long long value);
    
    /**
     * @brief Retorna a soma dos elementos de um intervalo.
     *
     * Complexidade: O(log n)
     *
     * @param left Limite esquerdo.
     * @param right Limite direito.
     *
     * @return Soma dos elementos.
     */
    [[nodiscard]]
    long long querySum(int left, int right);
    
    /**
     * @brief Retorna o menor elemento de um intervalo.
     *
     * Complexidade: O(log n)
     *
     * @param left Limite esquerdo.
     * @param right Limite direito.
     *
     * @return Menor valor encontrado.
     */
    [[nodiscard]]
    long long queryMin(int left, int right);
    
    /**
     * @brief Retorna o maior elemento de um intervalo.
     *
     * Complexidade: O(log n)
     *
     * @param left Limite esquerdo.
     * @param right Limite direito.
     *
     * @return Maior valor encontrado.
     */
    [[nodiscard]]
    long long queryMax(int left, int right);

    /**
     * @brief Retorna o valor armazenado em uma posição específica.
     *
     * Equivalente a consultar o intervalo [index, index].
     *
     * Complexidade: O(log n)
     *
     * @param index Índice desejado.
     *
     * @return Valor armazenado na posição.
     */
    [[nodiscard]]
    long long queryPoint(int index);


    /**
    * @brief Retorna os contadores da última operação executada.
    *
    * @return Referência constante para os contadores.
    */
    [[nodiscard]]
    const Counters& getCounters() const;

    /**
    * @brief Reinicia os contadores de operações primitivas.
    */
    void resetCounters();
};
