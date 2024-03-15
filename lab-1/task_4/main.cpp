#include "../matrix.h"
#include "functions.h"
#include <iostream>
#include <iomanip>
#include <string>
#include <cstring>
#include <stdexcept>


int ReadMatrixSize() {
    int n;
    std::cout << "Enter matrix size: ";
    std::cin >> n;

    if (n <= 0) {
        throw std::runtime_error("matrix size can't be negative or zero");
    }

    return n;
}


Matrix::TMatrix ReadMatrix() {
    int n = ReadMatrixSize();
    Matrix::TMatrix A(n, n);
    std::cout << "Enter matrix A:" << std::endl;
    Matrix::Read(A);
    return A;
}


float ReadEpsilon() {
    float eps;
    std::cout << "Enter precision: ";
    std::cin >> eps;

    if (eps < 0.0) {
        throw std::runtime_error("precision can't be a negativ value");
    }

    return eps;
}


std::tuple<float, float, float> ReadEpsilonRange() {
    float a, b, s;
    std::cout << "Enter epsilon range: ";
    std::cin >> a >> b >> s;

    if (a < 0.0) throw std::runtime_error("range start value can't be negative");
    if (b < 0.0) throw std::runtime_error("range end value can't be negative");
    if (s < 0.0) throw std::runtime_error("range step value can't be negative");

    return {a, b, s};
}


void PrintResult(const EigenTaskResult& result) {
    std::cout << "iterations: " << result.iterations << std::endl;

    std::cout << "eigen values: " << std::fixed;
    for (int i = 0; i < result.eigenValues.size(); ++i) {
        std::cout << std::setprecision(3) << result.eigenValues[i] << " ";
    }
    std::cout << std::endl;

    std::cout << "eigen vectors:" << std::endl;
    for (int i = 0; i < result.eigenVectors.size(); ++i) {
        std::cout << "x" << i << ": ";
        Matrix::Print(Matrix::Transpose(result.eigenVectors[i]));
    }
}


std::string Justify(const std::string& s, int length) {
    return s + std::string(std::max(0, int(length - s.length())), ' ');
}


void PrintStatisticTableHead() {
    std::cout << Justify("precision", 15) << " | " << Justify("iterations", 15) << std::endl;
}


void PrintStatisticEntry(float eps, int iterations) {
    std::cout << Justify(std::to_string(eps), 15) << " | " << Justify(std::to_string(iterations), 15) << std::endl;
}


bool IsInStatsMode(int argc, char* argv[]) {
    for (int i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "-s") == 0) {
            return true;
        }
    }
    return false;
}


int main(int argc, char* argv[]) {
    try {
        if (IsInStatsMode(argc, argv)) {
            std::tuple<float, float, float> range = ReadEpsilonRange();
            Matrix::TMatrix A = ReadMatrix();
            EigenTaskResult result;
            
            PrintStatisticTableHead();
            for (float eps = std::get<0>(range); eps <= std::get<1>(range); eps += std::get<2>(range)) {
                result = SolveEigenTask(A, eps);
                PrintStatisticEntry(eps, result.iterations);
            }
        }

        else {
            float eps = ReadEpsilon();
            Matrix::TMatrix A = ReadMatrix();
            EigenTaskResult result = SolveEigenTask(A, eps);
            PrintResult(result);
        }
    } catch (const std::exception& err) {
        std::cout << "error : " << err.what() << std::endl;
        exit(1);
    }

    return 0;
}
