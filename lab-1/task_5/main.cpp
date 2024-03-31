#include "../matrix.h"
#include "functions.h"
#include <iostream>


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
        throw std::runtime_error("precision can't be a negative value");
    }

    return eps;
}


void PrintEigenValues(const EigenValues& values) {
    for (const std::complex<float>& value : values) {
        if (value.imag() == 0.0) {
            std::cout << value.real() << std::endl;
        } else {
            std::cout << value.real();
            std::cout << ((value.imag() >= 0.0) ? " + " : " - ");
            std::cout << std::abs(value.imag()) << "i" << std::endl;
        }
    }
}


int main(void) {
    try {
        Matrix::TMatrix A = ReadMatrix();
        float eps = ReadEpsilon();
        EigenValues values = GetEigenValues(A, eps);

        std::cout << "Eigen values:" << std::endl;
        PrintEigenValues(values);
    } catch (const std::exception& err) {
        std::cout << "error : " << err.what() << std::endl;
        exit(1);
    }

    return 0;
}
