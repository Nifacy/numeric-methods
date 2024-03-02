#include <iomanip>
#include <iostream>
#include <vector>
#include <stdexcept>
#include "matrix.h"


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


void CalculateRunCoefficients(const Matrix::TMatrix& a, const Matrix::TMatrix& b, Matrix::TMatrix& result) {
    int n = std::get<0>(a.GetSize());

    for (int i = 0; i < n; ++i) {
        if (i == 0) {
            if (b.Get(i, 0) == 0.0) {
                throw std::runtime_error("Can't find solution of system");
            }

            result.Set(i, 0, - a.Get(i, 2) / a.Get(i, 1));
            result.Set(i, 1, b.Get(i, 0) / a.Get(i, 1));
        }
        
        else {
            float t = a.Get(i, 1) + a.Get(i, 0) * result.Get(i - 1, 0);

            if (t == 0.0) {
                throw std::runtime_error("Can't find solution of system");
            }

            result.Set(i, 0, - a.Get(i, 2) / t);
            result.Set(i, 1, (b.Get(i, 0) - a.Get(i, 0) * result.Get(i - 1, 1)) / t);
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


void SolveUsingRunCoefficients(const Matrix::TMatrix& runCoefs, Matrix::TMatrix& result) {
    int n = std::get<0>(runCoefs.GetSize());

    result.Set(n - 1, 0, runCoefs.Get(n - 1, 1));
    for (int i = n - 2; i >= 0; --i) {
        result.Set(i, 0, runCoefs.Get(i, 0) * result.Get(i + 1, 0) + runCoefs.Get(i, 1));
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
