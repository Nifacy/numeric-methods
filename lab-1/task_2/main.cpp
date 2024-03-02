#include "../matrix.h"
#include "functions.h"
#include <iostream>
#include <stdexcept>


void ReadTridiagonalMatrix(Matrix::TMatrix& a) {
    int n = std::get<0>(a.GetSize());
    float value;

    for (int i = 0; i < n; ++i) {
        if (i == 0) {
            a.Set(i, 0, 0.0);

            for (int j = 1; j < 3; ++j) {
                std::cin >> value;
                a.Set(i, j, value);
            }
        }
        
        else if (i == n - 1) {
            a.Set(i, 2, 0.0);

            for (int j = 0; j < 2; ++j) {
                std::cin >> value;
                a.Set(i, j, value);
            }
        }

        else {
            for (int j = 0; j < 3; ++j) {
                std::cin >> value;
                a.Set(i, j, value);
            }
        }
    }
}


void CheckCoefficients(const Matrix::TMatrix& a, const Matrix::TMatrix& b) {
    int n = std::get<0>(a.GetSize());

    for (int i = 0; i < n; ++i) {
        bool allZero = true;

        for (int j = 0; j < 3; ++i) {
            allZero = allZero && (a.Get(i, j) == 0.0);
        }

        if (allZero && b.Get(i, 0) != 0.0) {
            throw std::runtime_error("Can't find solution of system");
        }
    }
}


int ReadNumberOfEquations() {
    int n;
    std::cin >> n;

    if (n <= 0) {
        throw std::runtime_error("number can't be zero o negative");
    }

    return n;
}


int main() {
    try {
        std::cout << "Enter number of equations:" << std::endl;
        int n = ReadNumberOfEquations();

        Matrix::TMatrix a(n, 3);
        Matrix::TMatrix b(n, 1);
        Matrix::TMatrix runCoefs(n, 2);
        Matrix::TMatrix x(n, 1);

        std::cout << "Enter tridiagonal matrix's coefficients (matrix A):" << std::endl;
        ReadTridiagonalMatrix(a);

        std::cout << "Enter free coefficients (vector b):" << std::endl;
        Matrix::Read(b);

        CalculateRunCoefficients(a, b, runCoefs);
        SolveUsingRunCoefficients(runCoefs, x);

        std::cout << "Result:" << std::endl;
        Matrix::Print(x);
    
    } catch(const std::exception& err) {
        std::cout << "error : " << err.what() << std::endl;
        exit(1);
    }

    return 0;
}
