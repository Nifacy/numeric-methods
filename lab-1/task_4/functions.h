#ifndef _TASK_4_FUNCTIONS_
#define _TASK_4_FUNCTIONS_


#include "../matrix.h"
#include <vector>
#include <cmath>


struct EigenTaskResult {
    int iterations;
    std::vector<float> eigenValues;
    std::vector<Matrix::TMatrix> eigenVectors;
};


std::pair<int, int> FindMaxNotDiagonalElement(const Matrix::TMatrix& A) {
    int n = A.GetSize().first;
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
    if (aii == ajj) return M_PI / 4.0;
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
    return Matrix::Transpose(U) * A * U;
}


float t(const Matrix::TMatrix& A) {
    int n = A.GetSize().first;
    float s = 0.0, el;

    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            el = A.Get(i, j);
            s += el * el;
        }
    }

    return sqrt(s);
}


EigenTaskResult SolveEigenTask(const Matrix::TMatrix& M, float eps) {
    Matrix::TMatrix A(M);
    int n = A.GetSize().first;
    Matrix::TMatrix U = Matrix::TMatrix::Eye(n);
    EigenTaskResult result;
    result.iterations = 0;

    while (t(A) > eps) {
        std::pair<int, int> pos = FindMaxNotDiagonalElement(A);
        float phi = GetRotationAngle(A, pos.first, pos.second);
        Matrix::TMatrix u = GetRotationMatrix(n, pos.first, pos.second, phi);
        A = GetNextA(A, u);
        U = U * u;
        result.iterations++;
    }

    for (int i = 0; i < n; ++i) {
        result.eigenValues.push_back(A.Get(i, i));
    }

    for (int i = 0; i < n; ++i) {
        Matrix::TMatrix v(n, 1);
        for (int j = 0; j < n; ++j) {
            v.Set(j, 0, U.Get(j, i));
        }
        result.eigenVectors.push_back(v);
    }

    return result;
}


#endif // _TASK_4_FUNCTIONS_