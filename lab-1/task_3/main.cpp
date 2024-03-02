#include "../matrix.h"
#include "functions.h"
#include <iostream>


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

    JakobiMethod(m, b, alpha, beta);

    Matrix::Print(IterativeMethod(alpha, beta, 0.01));
    return 0;
}
