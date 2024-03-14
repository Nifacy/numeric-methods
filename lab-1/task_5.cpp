#include "matrix.h"
#include <iostream>
#include <cmath>
#include <complex>


void HouseholderMatrix(const Matrix::TMatrix& A, int i, Matrix::TMatrix& H) {
    int n = std::get<0>(A.GetSize());
    Matrix::TMatrix v(n, 1);

    for (int j = 0; j < n; ++j) {
        if (j < i)
            v.Set(j, 0, 0);
        else if (j > 0)
            v.Set(j, 0, A.Get(j, i));
        else {
            float aDiag = A.Get(i, i);
            float signA = float((aDiag > 0) - (aDiag < 0));
            float sum = 0.0;

            for (int t = j; t < n; ++t)
                sum += A.Get(t, i) * A.Get(t, i);

            v.Set(
                j, i,
                aDiag + signA * sqrt(sum)
            );
        }
    }

    float k = Matrix::Mult(Matrix::Transpose(v), v).Get(0, 0);

    Matrix::Mult(v, Matrix::Transpose(v), H);
    Matrix::Mult(H, -2.0 / k, H);
    Matrix::Add(H, Matrix::TMatrix::Eye(n), H);
}


void QRDecompose(const Matrix::TMatrix& A, Matrix::TMatrix& Q, Matrix::TMatrix& R) {
    int n = std::get<0>(A.GetSize());
    Matrix::TMatrix H(n, n);
    Q = Matrix::TMatrix::Eye(n);
    R = A;

    for (int i = 0; i < n - 1; ++i) {
        HouseholderMatrix(R, i, H);
        Q = Matrix::Mult(Q, H);
        R = Matrix::Mult(H, R);
    }
}


std::pair<std::complex<float>, std::complex<float>> FindComplexEigeValues(const Matrix::TMatrix& A, int i) {
    float a1 = A.Get(i, i), a2 = A.Get(i + 1, i + 1);
    float a3 = A.Get(i + 1, i), a4 = A.Get(i, i + 1);

    float b = - a1 - a2;
    float c = a1 * a2 - a3 * a4;

    float d = b * b - 4.0 * c;
    std::complex<float> dSqrt = std::sqrt(std::complex<float>(d, 0));

    return {
        std::complex<float>(0.5, 0.0) * (std::complex<float>(b, 0.0) - dSqrt),
        std::complex<float>(0.5, 0.0) * (std::complex<float>(b, 0.0) + dSqrt)
    };
}


float t(const Matrix::TMatrix& A, int i, int j) {
    int n = std::get<0>(A.GetSize());
    float sum = 0.0;

    for (int t = j; t < n; ++t) {
        sum += A.Get(t, i) * A.Get(t, i);
    }

    std::cout << "t(" << i << ", " << j << ") = " << std::sqrt(sum) << std::endl;
    return std::sqrt(sum);
}


float tComplex(const Matrix::TMatrix& Ai, int i) {
    int n = std::get<0>(Ai.GetSize());
    Matrix::TMatrix Q(n, n), R(n, n);

    QRDecompose(Ai, Q, R);
    Matrix::TMatrix ANext = Matrix::Mult(R, Q);

    auto lambda1 = FindComplexEigeValues(Ai, i);
    auto lambda2 = FindComplexEigeValues(ANext, i);

    return std::abs(lambda2.first - lambda1.first);
}


std::vector<std::complex<float>> GetEigenValues(const Matrix::TMatrix& A, float eps) {
    int n = std::get<0>(A.GetSize());
    Matrix::TMatrix Q(n, n), R(n, n);
    Matrix::TMatrix Ai = A;
    std::vector<std::complex<float>> values;
    int i = 0;

    while (i < n) {
        std::cout << "i: " << i << std::endl;
        std::cout << "A:" << std::endl;
        Matrix::Print(Ai);

        if (t(Ai, i, i + 1) <= eps) {
            values.push_back(Ai.Get(i, i));
            std::cout << "value: " << Ai.Get(i, i) << std::endl;
            i++;
            continue;
        }

        if ((t(Ai, i, i + 2) <= eps) && (tComplex(Ai, i) <= eps)) {
            auto p = FindComplexEigeValues(Ai, i);
            values.push_back(p.first);
            values.push_back(p.second);
            std::cout << "complex value (1): " << p.first << std::endl;
            std::cout << "complex value (2): " << p.second << std::endl;
            i += 2;
            continue;
        }

        QRDecompose(Ai, Q, R);
        Ai = Matrix::Mult(R, Q);
    }

    Matrix::Print(Ai);
    return values;
}


int main(void) {
    // Matrix::TMatrix A ({
    //     {1.0, 3.0, 1.0},
    //     {1.0, 1.0, 4.0},
    //     {4.0, 3.0, 1.0}
    // });

    Matrix::TMatrix A ({
        { -1.0, 2.0, 9.0},
        { 9.0, 3.0, 4.0 },
        {8 ,-4, -6}
    });

    GetEigenValues(A, 0.01);
    // QRDecompose(A, Q, R);

    // Matrix::Print(Q);
    // Matrix::Print(R);
}
