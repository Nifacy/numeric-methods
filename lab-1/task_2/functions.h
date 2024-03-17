#ifndef _TASK_2_FUNCTIONS_
#define _TASK_2_FUNCTIONS_

#include "../matrix.h"
#include <vector>
#include <stdexcept>


void CalculateRunCoefficients(const Matrix::TMatrix& a, const Matrix::TMatrix& b, Matrix::TMatrix& result) {
    int n = a.GetSize().first;

    for (int i = 0; i < n; ++i) {
        if (i == 0) {
            if (b.Get(i, 0) == 0.0) {
                throw std::runtime_error("Can't find solution of system");
            }

            result.Set(i, 0, - a.Get(i, 2) / a.Get(i, 1));
            result.Set(i, 1, b.Get(i, 0) / a.Get(i, 1));
        }
        
        else {
            float t = a.Get(i, 1) + a.Get(i, 0) * result.Get(i - 1, 0);

            if (t == 0.0) {
                throw std::runtime_error("Can't find solution of system");
            }

            result.Set(i, 0, - a.Get(i, 2) / t);
            result.Set(i, 1, (b.Get(i, 0) - a.Get(i, 0) * result.Get(i - 1, 1)) / t);
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
