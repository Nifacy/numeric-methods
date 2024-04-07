#ifndef _TASK_2_FUNCTIONS_
#define _TASK_2_FUNCTIONS_

#include "../matrix.h"
#include <vector>
#include <stdexcept>


void CalculateRunCoefficients(const Matrix::TMatrix& A, const Matrix::TMatrix& B, Matrix::TMatrix& result) {
    int n = A.GetSize().first;

    for (int i = 0; i < n; ++i) {
        float a = A.Get(i, 0), b = A.Get(i, 1), c = A.Get(i, 2);
        float d = B.Get(i, 0);

        if (i == 0) {
            if (B.Get(i, 0) == 0.0) {
                throw std::runtime_error("Can't find solution of system");
            }

            result.Set(i, 0, - c / b);
            result.Set(i, 1, d / b);
        }

        else {
            float PLast = result.Get(i - 1, 0), QLast = result.Get(i - 1, 1);
            float t = b + a * PLast;

            if (t == 0.0) {
                throw std::runtime_error("Can't find solution of system");
            }

            result.Set(i, 0, - c / t);
            result.Set(i, 1, (d - a * QLast) / t);
        }
    }
}


void SolveUsingRunCoefficients(const Matrix::TMatrix& runCoefs, Matrix::TMatrix& result) {
    int n = runCoefs.GetSize().first;

    result.Set(n - 1, 0, runCoefs.Get(n - 1, 1));
    for (int i = n - 2; i >= 0; --i) {
        result.Set(i, 0, runCoefs.Get(i, 0) * result.Get(i + 1, 0) + runCoefs.Get(i, 1));
    }
}


#endif // _TASK_2_FUNCTIONS_
