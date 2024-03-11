#include "../matrix.h"
#include "functions.h"
#include <iostream>
#include <iomanip>
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


int main(void) {
    Matrix::TMatrix A = ReadMatrix();
    float eps = ReadEpsilon();
    EigenTaskResult result = SolveEigenTask(A, eps);
    PrintResult(result);

    return 0;
}
