#ifndef _TASK_3_FUNCTIONS_
#define _TASK_3_FUNCTIONS_


#include "../matrix.h"
#include "../task_1/functions.h"
#include <cmath>


float Norm(const Matrix::TMatrix& m) {
    float matrixSum = 0.0;
    float element;
    int n = std::get<0>(m.GetSize());

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            element = m.Get(i, j);
            matrixSum += element * element;
        }
    }

    return std::sqrt(matrixSum);
}


void JakobiMethod(const Matrix::TMatrix& A, const Matrix::TMatrix& b, Matrix::TMatrix& alpha, Matrix::TMatrix& beta) {
    int n = std::get<0>(A.GetSize());
    float diag_alpha;

    for (int i = 0; i < n; ++i) {
        diag_alpha = A.Get(i, i);
        beta.Set(i, 0, b.Get(i, 0) / diag_alpha);

        for (int j = 0; j < n; ++j) {
            alpha.Set(
                i, j,
                (i == j) ? 0.0 : - A.Get(i, j) / diag_alpha
            );
        }
    }
}


float Epsilon(float alphaNorm, const Matrix::TMatrix& x1, const Matrix::TMatrix& x2) {
    float coef = alphaNorm / (1 - alphaNorm);
    Matrix::TMatrix diff = Matrix::Add(x1, Matrix::Mult(x2, -1.0));
    return coef * Norm(diff);
}


Matrix::TMatrix IterativeMethod(const Matrix::TMatrix& alpha, const Matrix::TMatrix& beta, float eps) {
    int n = std::get<0>(alpha.GetSize());
    float alphaNorm = Norm(alpha);
    int iterations = 0;

    Matrix::TMatrix x = beta;
    Matrix::TMatrix x2 = beta;

    while (true) {
        Matrix::Mult(alpha, x, x2);
        Matrix::Add(x2, beta, x2);

        if (Epsilon(alphaNorm, x, x2) <= eps) {
            return x2;
        }

        x = x2;
        iterations++;
    }
}


#endif // _TASK_3_FUNCTIONS_
