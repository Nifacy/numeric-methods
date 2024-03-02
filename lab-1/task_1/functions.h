#ifndef _TASK_1_FUNCTIONS_
#define _TASK_1_FUNCTIONS_

#include "../matrix.h"
#include <vector>
#include <algorithm>


void ForwardStep(Matrix::TMatrix& m, int k, std::vector<float>& coef) {
    int n = std::get<0>(m.GetSize());

    // try to find a string with a non-zero element
    // and swap it with the current
    if (m.Get(k, k) == 0.0) {
        bool found = false;

        for (int j = k + 1; j < n; ++j) {
            if (m.Get(j, k) != 0.0) {
                m.Swap(k, j);
                found = true;
                break;
            }
        }

        if (!found) {
            return;
        }
    }

    // convert raws below so that the elements are zero
    for (int i = k + 1; i < n; ++i) {
        float c = m.Get(i, k) / m.Get(k, k);

        for (int j = k; j < n; ++j) {
            m.Set(i, j, m.Get(i, j) - c * m.Get(k, j)); 
        }

        coef.push_back(c);
    }
}


void LUDecompose(const Matrix::TMatrix& a, Matrix::TMatrix& l, Matrix::TMatrix& u) {
    int n = std::get<0>(a.GetSize());
    std::vector<float> coef;

    l = Matrix::TMatrix::Eye(n);
    u = a;
    coef.reserve(n); // reserve max possible number of bytes to avoid allocations

    for (int k = 0; k < n - 1; ++k) {
        ForwardStep(u, k, coef);
        for (int i = 0; i < coef.size(); ++i) {
            l.Set(i + k + 1, k, coef[i]);
        }
        coef.clear();
    }
}


void SolveWithL(const Matrix::TMatrix& l, const std::vector<float>& b, std::vector<float>& x) {
    int n = std::get<0>(l.GetSize());

    for (int i = 0; i < n; ++i) {
        x[i] = b[i];
        for (int j = 0; j < i; ++j) {
            x[i] -= x[j] * l.Get(i, j);
        }
    }
}


void SolveWithU(const Matrix::TMatrix& u, const std::vector<float>& b, std::vector<float>& x) {
    int n = std::get<0>(u.GetSize());

    for (int i = n - 1; i >= 0; --i) {
        x[i] = b[i];

        for (int j = i + 1; j < n; ++j) {
            x[i] -= x[j] * u.Get(i, j);
        }

        x[i] /= u.Get(i, i);
    }
}


void SolveSystem(
    const Matrix::TMatrix& l,
    const Matrix::TMatrix& u,
    const std::vector<float>& b,
    std::vector<float>& x
) {
    std::vector<float> z(b.size(), 0.0);
    SolveWithL(l, b, z);
    SolveWithU(u, z, x);
}


float Determinant(const Matrix::TMatrix& l, const Matrix::TMatrix& u) {
    float d = 1.0;
    int n = std::get<0>(l.GetSize());

    for (int i = 0; i < n; ++i) {
        d *= u.Get(i, i);
    }

    return d;
}


void InverseMatrix(const Matrix::TMatrix& l, const Matrix::TMatrix& u, Matrix::TMatrix& r) {
    int n = std::get<0>(l.GetSize());
    std::vector<float> b(n, 0.0);
    std::vector<float> x(n, 0.0);

    for (int i = 0; i < n; ++i) {
        b[i] = 1.0;
        SolveSystem(l, u, b, x);

        for (int j = 0; j < n; ++j) {
            r.Set(j, i, x[j]);
        }

        b[i] = 0.0;
    }
}


#endif // _TASK_1_FUNCTIONS_
