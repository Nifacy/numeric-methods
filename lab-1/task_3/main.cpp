#include "../matrix.h"
#include "functions.h"
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>


using IterationMatrixCalculator = std::function<void(const Matrix::TMatrix&, const Matrix::TMatrix&, Matrix::TMatrix&, Matrix::TMatrix&)>;


IterationMatrixCalculator ReadIterationMethod() {
    std::cout << "Choose iteration method:" << std::endl;
    std::cout << "1. Jakobi method" << std::endl;
    std::cout << "2. Seidel method" << std::endl;

    int n;
    std::cin >> n;

    if (n == 1) {
        return JakobiMethod;
    }

    else if (n == 2) {
        return SeidelMethod;
    }

    throw std::runtime_error("unknown method's code " + std::to_string(n));
}


int ReadNumberOfEquations() {
    int n;
    std::cin >> n;

    if (n <= 0) {
        throw std::runtime_error("number can't be zero o negative");
    }

    return n;
}


int ReadAccuracy() {
    float eps;
    std::cin >> eps;

    if (eps <= 0) {
        throw std::runtime_error("accuracy can't be zero o negative");
    }

    return eps;
}


int main() {
    try {
        std::cout << "Enter number of equations: ";
        int n = ReadNumberOfEquations();

        Matrix::TMatrix A(n, n), b(n, 1), alpha(n, n), beta(n, 1);

        std::cout << "Enter matrix A:" << std::endl;
        Matrix::Read(A);

        std::cout << "Enter matrix b:" << std::endl;
        Matrix::Read(b);

        IterationMatrixCalculator method = ReadIterationMethod();

        std::cout << "Enter accuracy: ";
        float eps = ReadAccuracy();

        method(A, b, alpha, beta);
        IterativeMethodResult result = IterativeMethod(alpha, beta, eps);

        std::cout << "Result:" << std::endl;
        Matrix::Print(result.result);
        std::cout << "Iterations: " << result.iterations << std::endl;
    } catch (const std::exception& err) {
        std::cout << "error : " << err.what() << std::endl;
        exit(1);
    }

    return 0;
}
