#ifndef _TASK_3_FUNCTIONS_
#define _TASK_3_FUNCTIONS_


#include "../matrix.h"
#include "../task_1/functions.h"
#include <cmath>


struct IterativeMethodResult {
    Matrix::TMatrix result;
    int iterations;
};


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
    float diagAlpha;

    for (int i = 0; i < n; ++i) {
        diagAlpha = A.Get(i, i);
        beta.Set(i, 0, b.Get(i, 0) / diagAlpha);

        for (int j = 0; j < n; ++j) {
            alpha.Set(
                i, j,
                (i == j) ? 0.0 : - A.Get(i, j) / diagAlpha
            );
        }
    }
}


void inverseMatrix(const Matrix::TMatrix& m, Matrix::TMatrix& result) {
    int n = std::get<0>(m.GetSize());
    Matrix::TMatrix l(n, n), u(n, n);

    LUDecompose(m, l, u);
    InverseMatrix(l, u, result);
}


void SeidelMethod(const Matrix::TMatrix& A, const Matrix::TMatrix& b, Matrix::TMatrix& alpha, Matrix::TMatrix& beta) {
    int n = std::get<0>(A.GetSize());
    Matrix::TMatrix B(n, n), C(n, n), T(n, n);
    Matrix::TMatrix E = Matrix::TMatrix::Eye(n);

    JakobiMethod(A, b, alpha, beta);

    // split alpha matrix B, C: alpha = B + C
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            if (j >= i) C.Set(i, j, alpha.Get(i, j));
            else B.Set(i, j, alpha.Get(i, j));
        }
    }

    inverseMatrix(Matrix::Add(E, Matrix::Mult(B, -1.0)), T);
    alpha = Matrix::Mult(T, C);
    beta = Matrix::Mult(T, beta);
}


float Epsilon(float alphaNorm, const Matrix::TMatrix& x1, const Matrix::TMatrix& x2) {
    float coef = alphaNorm / (1 - alphaNorm);
    Matrix::TMatrix diff = Matrix::Add(x1, Matrix::Mult(x2, -1.0));
    return coef * Norm(diff);
}


IterativeMethodResult IterativeMethod(const Matrix::TMatrix& alpha, const Matrix::TMatrix& beta, float eps) {
    int n = std::get<0>(alpha.GetSize());
    float alphaNorm = Norm(alpha);
    int iterations = 0;

    Matrix::TMatrix x = beta;
    Matrix::TMatrix x2 = beta;

    while (true) {
        iterations++;
        Matrix::Mult(alpha, x, x2);
        Matrix::Add(x2, beta, x2);

        if (Epsilon(alphaNorm, x, x2) <= eps) {
            break;
        }

        x = x2;
    }

    return {
        .result=x2,
        .iterations=iterations
    };
}


#endif // _TASK_3_FUNCTIONS_
