#include "../matrix.h"
#include <cmath>
#include <iostream>


std::pair<int, int> FindMaxNotDiagonalElement(const Matrix::TMatrix& A) {
    int n = std::get<0>(A.GetSize());
    int maxI = 0, maxJ = 1;

    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            if (fabsf(A.Get(i, j)) > fabsf(A.Get(maxI, maxJ))) {
                maxI = i;
                maxJ = j;
            }
        }
    }

    return {maxI, maxJ};
}


float GetRotationAngle(const Matrix::TMatrix& A, int i, int j) {
    float aii = A.Get(i, i), ajj = A.Get(j, j), aij = A.Get(i, j);
    if (aii == ajj) return M_PI / 2.0;
    return 0.5 * atan((2.0 * aij) / (aii - ajj));
}


Matrix::TMatrix GetRotationMatrix(int n, int i, int j, float phi) {
    Matrix::TMatrix U = Matrix::TMatrix::Eye(n);
    float c = cos(phi), s = sin(phi);
    U.Set(i, i, c);
    U.Set(j, j, c);
    U.Set(i, j, -s);
    U.Set(j, i, s);
    return U;
}


Matrix::TMatrix GetNextA(const Matrix::TMatrix& A, const Matrix::TMatrix& U) {
    return Matrix::Mult(
        Matrix::Mult(
            Matrix::Transpose(U),
            A
        ),
        U
    );
}


float t(const Matrix::TMatrix& A) {
    int n = std::get<0>(A.GetSize());
    float s = 0.0, el;

    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            el = A.Get(i, j);
            s += el * el;
        }
    }

    return sqrt(s);
}


int main(void) {
    int n = 3;
    float eps = 0.0001;
    Matrix::TMatrix A({
        {4.0, 2.0, 1.0},
        {2.0, 5.0, 3.0},
        {1.0, 3.0, 6.0}
    });

    Matrix::TMatrix U = Matrix::TMatrix::Eye(n);
    int k = 0;

    while (t(A) > eps) {
        std::cout << "k = " << k << std::endl;
        
        std::cout << "A(" << k << ")" << std::endl;
        Matrix::Print(A);
        std::cout << std::endl;

        std::pair<int, int> x = FindMaxNotDiagonalElement(A);
        std::cout << "a(" << x.first << ", " << x.second << ") = " << A.Get(x.first, x.second) << std::endl;
        
        float phi = GetRotationAngle(A, x.first, x.second);
        std::cout << "phi(" << k << ") = " << phi << std::endl;
        
        Matrix::TMatrix u = GetRotationMatrix(3, x.first, x.second, GetRotationAngle(A, x.first, x.second));
        std::cout << "U(" << k << "):" << std::endl;
        Matrix::Print(u);
        
        A = GetNextA(A, u);
        U = Matrix::Mult(U, u);
        k++;
    }

    std::cout << "--- RESULT ---" << std::endl;
    std::cout << "iterations: " << k << std::endl;
    std::cout << "eigenvalues: ";

    for (int i = 0; i < n; ++i) {
        std::cout << std::setprecision(3) << A.Get(i, i) << " ";
    }

    std::cout << std::endl;

    std::cout << "eigenvectors:" << std::endl;

    for (int i = 0; i < n; ++i) {
        std::cout << "x" << i << ": ";
        for (int j = 0; j < n; ++j) {
            std::cout << std::setprecision(3) << U.Get(j, i) << " ";
        }
        std::cout << std::endl;
    }

    return 0;
}
