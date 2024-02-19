#include <iostream>
#include "matrix.h"
#include <algorithm>
#include <iomanip>
#include <stdexcept>


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


int ReadNumberOfEquations() {
    int n;
    std::cin >> n;

    if (n <= 0) {
        throw std::runtime_error("number can't be zero o negative");
    }

    return n;
}


void ReadVector(std::vector<float>& v) {
    for (float& el: v) {
        std::cin >> el;
    }
}


void CheckDeterminant(float d) {
    if (d == 0.0) {
        throw std::runtime_error("matrix can't be a singular");
    }
}


int main(void) {
    try {
        std::cout << "Enter number of equations: ";
        int n = ReadNumberOfEquations();

        Matrix::TMatrix a(n, n);
        Matrix::TMatrix l(n, n), u(n, n);
        Matrix::TMatrix inversed(n, n);

        std::vector<float> b(n, 0.0);
        std::vector<float> x(n, 0.0);

        float d;

        // Read input data
        std::cout << "Enter matrix A:" << std::endl;
        Matrix::Read(a);
        std::cout << "Enter vector b:" << std::endl;
        ReadVector(b);

        // decompose matrix
        LUDecompose(a, l, u);

        // solve system
        SolveSystem(l, u, b, x);

        // find determinant
        d = Determinant(l, u);
        CheckDeterminant(d);

        // find inversed matrix
        InverseMatrix(l, u, inversed);

        // print results
        std::cout << "LU decompose:" << std::endl;
        std::cout << "L:" << std::endl;
        Matrix::Print(l);
        std::cout << "U:" << std::endl;
        Matrix::Print(u);

        std::cout << "\nSolution: x = [ ";
        for (const float el: x) {
            std::cout << std::setprecision(3) << el << " ";
        }
        std::cout << "]" << std::endl;

        std::cout << "\nDeterminant of A: det(A) = ";
        std::cout << std::setprecision(3) << d << std::endl;

        std::cout << "\nInversed matrix A:" << std::endl;
        Matrix::Print(inversed);
    
    } catch (const std::exception& err) {
        std::cout << "error : " << err.what() << std::endl;
        exit(1);
    }

    return 0;
}
