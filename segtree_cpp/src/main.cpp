#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <fstream>

#include "../include/SegmentTree.h"

enum class OperationType {
    QuerySum,
    QueryMin,
    QueryMax,
    UpdateRange,
    UpdatePoint
};

/**
 * @brief Representa uma operação que será executada na Segment Tree.
 */
struct Operation {

    OperationType type;

    int left = 0;
    int right = 0;
    int index = 0;
    long long value = 0;
};

/**
 * @brief Armazena todos os dados lidos da entrada.
 */
struct InputData {

    int n;
    int m;

    std::vector<long long> values;
    std::vector<Operation> operations;
};


/**
 * @brief Lê e interpreta toda a entrada recebida pela stdin.
 *
 * Formato esperado:
 *
 * N M
 * v1 v2 ... vN
 * operação1
 * operação2
 * ...
 *
 * Cada comando "query" é convertido em três operações:
 * QuerySum, QueryMin e QueryMax,
 * exatamente como na implementação em Python.
 */
InputData readInput() {

    InputData data;

    std::cin >> data.n >> data.m;

    data.values.resize(data.n);

    for (int i = 0; i < data.n; i++) {
        std::cin >> data.values[i];
    }

    std::string command;

    while (std::cin >> command) {

        if (command == "query") {

            int l, r;
            std::cin >> l >> r;

            Operation op;

            op.left = l;
            op.right = r;

            op.type = OperationType::QuerySum;
            data.operations.push_back(op);

            op.type = OperationType::QueryMin;
            data.operations.push_back(op);

            op.type = OperationType::QueryMax;
            data.operations.push_back(op);
        }

        else if (command == "update_range") {

            int l, r;
            long long value;

            std::cin >> l >> r >> value;

            Operation op;

            op.type = OperationType::UpdateRange;
            op.left = l;
            op.right = r;
            op.value = value;

            data.operations.push_back(op);
        }

        else if (command == "update_point") {

            int index;
            long long value;

            std::cin >> index >> value;

            Operation op;

            op.type = OperationType::UpdatePoint;
            op.index = index;
            op.value = value;

            data.operations.push_back(op);
        }
    }

    return data;
}

/**
 * @brief Imprime uma linha no formato CSV esperado pelo Orquestrador.
 *
 * Formato:
 * "language,n,m,load,input_file,ops_executed,op,time_ns,primitives
 */
void emit(const std::string& language,
          int n,
          int m,
          const std::string& load,
          const std::string& inputFile,
          int opsExecuted,
          const std::string& operation,
          long long timeNs,
          uint64_t primitives)
{
    std::cout
        << language << ","
        << n << ","
        << m << ","
        << load << ","
        << inputFile << ","
        << opsExecuted << ","
        << operation << ","
        << timeNs << ","
        << primitives
        << '\n';
}






int main(int argc, char* argv[]) {

    std::string inputFile;
    std::string load = "query";
    int warmup = 1;
    int repetitions = 1;

    for (int i = 1; i < argc; i++) {

        std::string argument = argv[i];

        if (argument == "--input" && i + 1 < argc) {
            inputFile = argv[++i];
        }

        else if (argument == "--load" && i + 1 < argc) {
            load = argv[++i];
        }

        else if (argument == "--warmup" && i + 1 < argc) {
            warmup = std::stoi(argv[++i]);
        }

        else if (argument == "--repetitions" && i + 1 < argc) {
            repetitions = std::stoi(argv[++i]);
        }
    }

    std::ifstream file(inputFile);

    if (!file.is_open()) {
        std::cerr << "Erro ao abrir arquivo: " << inputFile << '\n';
        return 1;
    }

    if (inputFile.empty()) {
        std::cerr << "Erro: Parâmetro obrigatório --input não especificado.\n";
        return 1;
    }

    std::cin.rdbuf(file.rdbuf());

    InputData data = readInput();

    std::vector<Operation> loadOperations;

    if (load == "query") {

        for (const Operation& operation : data.operations) {

            if (operation.type == OperationType::QuerySum ||
                operation.type == OperationType::QueryMin ||
                operation.type == OperationType::QueryMax) {

                loadOperations.push_back(operation);
            }
        }
    }

    else if (load == "update") {

        for (const Operation& operation : data.operations) {

            if (operation.type == OperationType::UpdateRange ||
                operation.type == OperationType::UpdatePoint) {

                loadOperations.push_back(operation);
            }
        }
    }

    else if (load == "mixed") {

        loadOperations = data.operations;
    }

    else {

        std::cerr << "Parametro --load invalido.\n";
        return 1;
    }

    for (int i = 0; i < warmup; i++) {

        SegmentTree segmentTree(data.values);

        for (const Operation& operation : loadOperations) {

            switch (operation.type) {

                case OperationType::QuerySum:
                    segmentTree.querySum(operation.left, operation.right);
                    break;

                case OperationType::QueryMin:
                    segmentTree.queryMin(operation.left, operation.right);
                    break;

                case OperationType::QueryMax:
                    segmentTree.queryMax(operation.left, operation.right);
                    break;

                case OperationType::UpdateRange:
                    segmentTree.updateRange(
                        operation.left,
                        operation.right,
                        operation.value
                    );
                    break;

                case OperationType::UpdatePoint:
                    segmentTree.updatePoint(
                        operation.index,
                        operation.value
                    );
                    break;
        }
    }
}

for (int i = 0; i < repetitions; i++) {

    auto buildStart = std::chrono::high_resolution_clock::now();

    SegmentTree segmentTree(data.values);

    auto buildEnd = std::chrono::high_resolution_clock::now();

    long long buildTime =
        std::chrono::duration_cast<std::chrono::nanoseconds>(
            buildEnd - buildStart
        ).count();

    emit(
        "cpp",
        data.n,
        data.m,
        load,
        inputFile,
        static_cast<int>(loadOperations.size()),
        "build",
        buildTime,
        segmentTree.getCounters().visitedNodes
    );

    for (const Operation& operation : loadOperations) {

        segmentTree.resetCounters();

        auto start = std::chrono::high_resolution_clock::now();

        std::string operationName;

        switch (operation.type) {

            case OperationType::QuerySum:
                segmentTree.querySum(operation.left, operation.right);
                operationName = "query_sum";
                break;

            case OperationType::QueryMin:
                segmentTree.queryMin(operation.left, operation.right);
                operationName = "query_min";
                break;

            case OperationType::QueryMax:
                segmentTree.queryMax(operation.left, operation.right);
                operationName = "query_max";
                break;

            case OperationType::UpdateRange:
                segmentTree.updateRange(
                    operation.left,
                    operation.right,
                    operation.value
                );
                operationName = "update_range";
                break;

            case OperationType::UpdatePoint:
                segmentTree.updatePoint(
                    operation.index,
                    operation.value
                );
                operationName = "update_point";
                break;
        }

        auto end = std::chrono::high_resolution_clock::now();

        long long elapsedTime =
            std::chrono::duration_cast<std::chrono::nanoseconds>(
                end - start
            ).count();

        emit(
            "cpp",
            data.n,
            data.m,
            load,
            inputFile,
            static_cast<int>(loadOperations.size()),
            operationName,
            elapsedTime,
            segmentTree.getCounters().visitedNodes
            );
        }
    }
    return 0;
}
