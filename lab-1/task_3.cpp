#include "./matrix.h"
#include <iostream>
#include <cmath>


using namespace std;


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

    return sqrt(matrixSum);
}


void Jakobi(const Matrix::TMatrix& A, const Matrix::TMatrix& b, Matrix::TMatrix& alpha, Matrix::TMatrix& beta) {
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


int main() {
    Matrix::TMatrix m(3, 3);
    m.Set(0, 0, 10.0);
    m.Set(0, 1, 1.0);
    m.Set(0, 2, 1.0);
    m.Set(1, 0, 2.0);
    m.Set(1, 1, 10.0);
    m.Set(1, 2, 1.0);
    m.Set(2, 0, 2.0);
    m.Set(2, 1, 2.0);
    m.Set(2, 2, 10.0);

    Matrix::TMatrix b(3, 1);
    b.Set(0, 0, 12.0);
    b.Set(1, 0, 13.0);
    b.Set(2, 0, 14.0);

    Matrix::TMatrix alpha(3, 3);
    Matrix::TMatrix beta(3, 1);
    Matrix::TMatrix x(3, 1);

    Jakobi(m, b, alpha, beta);

    Matrix::Print(IterativeMethod(alpha, beta, 0.01));
    return 0;
}
