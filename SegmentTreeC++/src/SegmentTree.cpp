#include "../include/SegmentTree.h"

#include <climits>
#include <algorithm>
#include <stdexcept>
#include <string>


// Constructor
SegmentTree::SegmentTree(const std::vector<long long>& arr)
    : n(arr.size()) 
    {
    
    if (n == 0) {
        throw std::invalid_argument("Não pode se construir uma SegmentTree com vector vazio.");
    }

    sumTree.resize(4 * n);
    maxTree.resize(4 * n);
    minTree.resize(4 * n);
    lazy.resize(4 * n);
    build(arr, 1, 0, n - 1);
}

// Private helper functions
void SegmentTree::build(const std::vector<long long> &arr, int node, int start, int end) {
    if (start == end) {
        sumTree[node] = arr[start];
        maxTree[node] = arr[start];
        minTree[node] = arr[start];
    }
    else {
        int mid = start + (end - start) / 2;
        build(arr, 2 * node, start, mid);
        build(arr, 2 * node + 1, mid + 1, end);
        pull(node);
    }
}

void SegmentTree::pull(int node) {
    sumTree[node] = sumTree[2 * node] + sumTree[2 * node + 1];
    minTree[node] = min(minTree[2 * node], minTree[2 * node + 1]);
    maxTree[node] = max(maxTree[2 * node], maxTree[2 * node + 1]);
}

void SegmentTree::push(int node, int start, int end) {
    if (lazy[node] != 0) {
        int mid = start + (end - start) / 2;
        applyLazy(2 * node, start, mid, lazy[node]);
        applyLazy(2 * node + 1, mid + 1, end, lazy[node]);
        lazy[node] = 0;
    }
}

// Apply lazy propagation
void SegmentTree::applyLazy(int node, int start, int end, long long value) {
    sumTree[node] += value * (end - start + 1);
    minTree[node] += value;
    maxTree[node] += value;
    lazy[node] += value;
}


// Update functions
void SegmentTree::updatePoint(int index, long long value) {
    validateIndex(index);
    updatePoint(1, 0, n - 1, index, value);
}

void SegmentTree::updatePoint(int node, int start, int end, int index, long long value) {
    if (start == end) {
        sumTree[node] = value;
        minTree[node] = value;
        maxTree[node] = value;
    }
    else {
        push(node, start, end);
        int mid = start + (end - start) / 2;
        if (index <= mid) {
            updatePoint(2 * node, start, mid, index, value);
        }
        else {
            updatePoint(2 * node + 1, mid + 1, end, index, value);
        }
        pull(node);
    }
}


void SegmentTree::updateRange(int left, int right, long long value) {
    validateRange(left, right);
    updateRange(1, 0, n - 1, left, right, value);
}

void SegmentTree::updateRange(int node, int start, int end, int left, int right, long long value) {
    if (right < start || end < left) {
        return;
    }
    if (left <= start && end <= right) {
        applyLazy(node, start, end, value);
        return;
    }
    push(node, start, end);
    int mid = start + (end - start) / 2;
    updateRange(2 * node, start, mid, left, right, value);
    updateRange(2 * node + 1, mid + 1, end, left, right, value);
    pull(node);
}



// Query functions
long long SegmentTree::querySum(int left, int right) {
    validateRange(left, right);
    return querySum(1, 0, n - 1, left, right);
}

long long SegmentTree::querySum(int node, int start, int end, int left, int right) {
    if (right < start || end < left)
    {
        return 0;
    }
    if (left <= start && end <= right) {
        return sumTree[node];
    }
    push(node, start, end);
    int mid = start + (end - start) / 2;
    long long sumLeft = querySum(2 * node, start, mid, left, right);
    long long sumRight = querySum(2 * node + 1, mid + 1, end, left, right);
    return sumLeft + sumRight;
}



long long SegmentTree::queryMin(int left, int right) {
    validateRange(left, right);
    return queryMin(1, 0, n - 1, left, right);
}

long long SegmentTree::queryMin(int node, int start, int end, int left, int right) {
    if (right < start || end < left) {
        return LLONG_MAX;
    }
    if (left <= start && end <= right) {
        return minTree[node];
    }
    push(node, start, end);
    int mid = start + (end - start) / 2;
    long long minLeft = queryMin(2 * node, start, mid, left, right);
    long long minRight = queryMin(2 * node + 1, mid + 1, end, left, right);
    return min(minLeft, minRight);
}



long long SegmentTree::queryMax(int left, int right) {
    validateRange(left, right);
    return queryMax(1, 0, n - 1, left, right);
}

long long SegmentTree::queryMax(int node, int start, int end, int left, int right) {
    if (right < start || end < left) {
        return LLONG_MIN;
    }
    if (left <= start && end <= right) {
        return maxTree[node];
    }
    push(node, start, end);
    int mid = start + (end - start) / 2;
    long long maxLeft = queryMax(2 * node, start, mid, left, right);
    long long maxRight = queryMax(2 * node + 1, mid + 1, end, left, right);
    return max(maxLeft, maxRight);
}



long long SegmentTree::queryPoint(int index) {
    validateIndex(index);
    return querySum(index, index);
}


// Validation functions
void SegmentTree::validateIndex(int index)
{
    if (index < 0 || index >= n) {
        throw std::out_of_range("Índice fora do intervalo válido: " + std::to_string(index));
    }
}

void SegmentTree::validateRange(int left, int right) {
    if (left < 0 || right >= n || left > right){
        throw std::out_of_range("Intervalo inválido: [" + std::to_string(left) + ", " + std::to_string(right) + "]");
    }
}
