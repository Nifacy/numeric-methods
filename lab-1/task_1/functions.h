#ifndef _TASK_1_FUNCTIONS_
#define _TASK_1_FUNCTIONS_

#include "../matrix.h"
#include <vector>
#include <algorithm>


std::pair<int, int> ForwardStep(Matrix::TMatrix& m, int k, std::vector<float>& coef) {
    int n = m.GetSize().first;

    // find element with maximum square to avoid small dividers
    int swapIndex = k;

    for (int i = k + 1; i < n; ++i) {
        float a = m.Get(swapIndex, k);
        float b = m.Get(i, k);

        if (a * a > b * b) {
            swapIndex = i;
        }
    }

    m.SwapRaws(k, swapIndex);

    // try to find a string with a non-zero element
    // and swap it with the current
    if (m.Get(k, k) == 0.0) {
        return {k, k};
    }

    // convert raws below so that the elements are zero
    for (int i = k + 1; i < n; ++i) {
        float c = m.Get(i, k) / m.Get(k, k);

        for (int j = k; j < n; ++j) {
            m.Set(i, j, m.Get(i, j) - c * m.Get(k, j)); 
        }

        coef.push_back(c);
    }

    return {k, swapIndex};
}


void LUDecompose(const Matrix::TMatrix& a, Matrix::TMatrix& l, Matrix::TMatrix& u, Matrix::TMatrix& p) {
    int n = a.GetSize().first;
    std::vector<float> coef;

    p = Matrix::TMatrix::Eye(n);
    l = Matrix::TMatrix::Eye(n);
    u = a;

    coef.reserve(n); // reserve max possible number of bytes to avoid allocations

    for (int k = 0; k < n - 1; ++k) {
        std::pair<int, int> swap = ForwardStep(u, k, coef);

        for (int i = 0; i < coef.size(); ++i) {
            l.Set(i + k + 1, k, coef[i]);
        }

        p.SwapRaws(swap.first, swap.second);

        coef.clear();
    }
}


void SolveWithL(const Matrix::TMatrix& l, const Matrix::TMatrix& b, Matrix::TMatrix& x) {
    int n = l.GetSize().first;

    for (int i = 0; i < n; ++i) {
        float c = b.Get(i, 0);
        for (int j = 0; j < i; ++j) {
            c -= x.Get(j, 0) * l.Get(i, j);
        }
        x.Set(i, 0, c);
    }
}


void SolveWithU(const Matrix::TMatrix& u, const Matrix::TMatrix& b, Matrix::TMatrix& x) {
    int n = u.GetSize().first;

    for (int i = n - 1; i >= 0; --i) {
        float c = b.Get(i, 0);

        for (int j = i + 1; j < n; ++j) {
            c -= x.Get(j, 0) * u.Get(i, j);
        }

        c /= u.Get(i, i);
        x.Set(i, 0, c);
    }
}


void SolveSystem(
    const Matrix::TMatrix& l,
    const Matrix::TMatrix& u,
    const Matrix::TMatrix& b,
    Matrix::TMatrix& x
) {
    Matrix::TMatrix z(b.GetSize().first, 1);
    SolveWithL(l, b, z);
    SolveWithU(u, z, x);
}


float Determinant(const Matrix::TMatrix& l, const Matrix::TMatrix& u) {
    float d = 1.0;
    int n = l.GetSize().first;

    for (int i = 0; i < n; ++i) {
        d *= u.Get(i, i);
    }

    return d;
}


void InverseMatrix(const Matrix::TMatrix& l, const Matrix::TMatrix& u, const Matrix::TMatrix& p, Matrix::TMatrix& r) {
    int n = l.GetSize().first;
    Matrix::TMatrix b(n, 1);
    Matrix::TMatrix x(n, 1);

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            b.Set(j, 0, p.Get(j, i));
        }

        SolveSystem(l, u, b, x);

        for (int j = 0; j < n; ++j) {
            r.Set(j, i, x.Get(j, 0));
        }
    }
}


#endif // _TASK_1_FUNCTIONS_
