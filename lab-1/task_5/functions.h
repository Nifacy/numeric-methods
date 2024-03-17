#ifndef _TASK_5_FUNCTIONS_
#define _TASK_5_FUNCTIONS_

#include "../matrix.h"
#include <vector>
#include <complex>


using ComplexPair = std::pair<std::complex<float>, std::complex<float>>;
using EigenValues = std::vector<std::complex<float>>;
using ChangeHistory = std::vector<float>;


const int HISTORY_SIZE = 5;


void GetHouseholderMatrix(const Matrix::TMatrix& A, int i, Matrix::TMatrix& H) {
    int n = A.GetSize().first;
    Matrix::TMatrix v(n, 1);

    for (int j = 0; j < n; ++j) {
        if (j < i) {
            v.Set(j, 0, 0);
        }

        else if (j > 0) {
            v.Set(j, 0, A.Get(j, i));
        }

        else {
            float aDiag = A.Get(i, i);
            float signA = float((aDiag > 0) - (aDiag < 0));
            float sum = 0.0;

            for (int t = j; t < n; ++t) {
                sum += A.Get(t, i) * A.Get(t, i);
            }

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
    int n = A.GetSize().first;
    Matrix::TMatrix H(n, n);
    Q = Matrix::TMatrix::Eye(n);
    R = A;

    for (int i = 0; i < n - 1; ++i) {
        GetHouseholderMatrix(R, i, H);
        Q = Matrix::Mult(Q, H);
        R = Matrix::Mult(H, R);
    }
}


ComplexPair FindComplexEigeValues(const Matrix::TMatrix& A, int i) {
    float a1 = A.Get(i, i), a2 = A.Get(i + 1, i + 1);
    float a3 = A.Get(i + 1, i), a4 = A.Get(i, i + 1);

    float b = - a1 - a2;
    float c = a1 * a2 - a3 * a4;
    float d = b * b - 4.0 * c;

    std::complex<float> dSqrt = std::sqrt(std::complex<float>(d, 0));
    std::complex<float> bComplex = std::complex<float>(b, 0.0);
    std::complex<float> k = 0.5;

    return { k * (-bComplex + dSqrt), k * (-bComplex - dSqrt) };
}


bool tReal(const Matrix::TMatrix& A, int i, int j, float eps) {
    int n = A.GetSize().first;
    float sum = 0.0;

    for (int t = j; t < n; ++t) {
        sum += A.Get(t, i) * A.Get(t, i);
    }

    return std::sqrt(sum) <= eps;
}


float tComplex(const Matrix::TMatrix& Ai, int i, float eps) {
    int n = Ai.GetSize().first;
    Matrix::TMatrix Q(n, n), R(n, n);

    QRDecompose(Ai, Q, R);
    Matrix::TMatrix ANext = Matrix::Mult(R, Q);

    ComplexPair lambda1 = FindComplexEigeValues(Ai, i);
    ComplexPair lambda2 = FindComplexEigeValues(ANext, i);

    return (std::abs(lambda2.first - lambda1.first) <= eps) && (std::abs(lambda2.second - lambda1.second) <= eps);
}


bool IsEigenValueReal(const ChangeHistory& history) {
    int startIndex = std::max(1, int(history.size()) - HISTORY_SIZE);

    for (int i = startIndex; i < history.size(); ++i) {
        if (history[i] >= history[i - 1]) {
            return false;
        }
    }
    return true;
}


void UpdateChangeHistory(const Matrix::TMatrix& A, std::vector<ChangeHistory>& history) {
    int n = A.GetSize().first;

    for (int i = 0; i < n - 1; ++i) {
        history[i].push_back(std::abs(A.Get(i + 1, i)));
    }
}


EigenValues GetEigenValues(const Matrix::TMatrix& A, float eps) {
    int n = A.GetSize().first;
    Matrix::TMatrix Q(n, n), R(n, n);
    Matrix::TMatrix Ai = A;
    EigenValues values;
    std::vector<std::vector<float>> history(n);
    int i = 0;

    while (i < n) {
        QRDecompose(Ai, Q, R);
        Ai = Matrix::Mult(R, Q);
        UpdateChangeHistory(Ai, history);

        if (IsEigenValueReal(history[i])) {
            if (tReal(Ai, i, i + 1, eps)) {
                values.push_back(Ai.Get(i, i));
                i++;
            }
        } else {
            if (tReal(Ai, i, i + 2, eps) && tComplex(Ai, i, eps)) {
                ComplexPair p = FindComplexEigeValues(Ai, i);
                values.push_back(p.first);
                values.push_back(p.second);
                i += 2;
            }
        }
    }

    return values;
}


#endif // _TASK_5_FUNCTIONS_
