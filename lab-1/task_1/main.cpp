#include "../matrix.h"
#include "functions.h"
#include <iostream>
#include <iomanip>
#include <stdexcept>


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
        Matrix::TMatrix l(n, n), u(n, n), p(n, n);
        Matrix::TMatrix inversed(n, n);

        Matrix::TMatrix b(n, 1);
        Matrix::TMatrix x(n, 1);

        float d;

        // Read input data
        std::cout << "Enter matrix A:" << std::endl;
        Matrix::Read(a);
        std::cout << "Enter vector b:" << std::endl;
        Matrix::Read(b);

        // decompose matrix
        LUDecompose(a, l, u, p);

        // solve system
        SolveSystem(l, u, p, b, x);

        // find determinant
        d = Determinant(l, u, p);
        CheckDeterminant(d);

        // find inversed matrix
        InverseMatrix(l, u, p, inversed);

        // print results
        std::cout << "LU decompose:" << std::endl;
        std::cout << "L:" << std::endl;
        Matrix::Print(l);
        std::cout << "U:" << std::endl;
        Matrix::Print(u);
        std::cout << "Permutation matrix:" << std::endl;
        Matrix::Print(p);

        std::cout << "\nSolution: x: ";
        Matrix::Print(Matrix::Transpose(x));

        std::cout << "\nDeterminant of A: det(A) = ";
        std::cout << std::setprecision(3) << d << std::endl;

        std::cout << "\nInversed matrix A:" << std::endl;
        Matrix::Print(inversed);

        std::cout << "\n--- CHECKS ---\n" << std::endl;

        std::cout << "L * U:" << std::endl;
        Matrix::Print(l * u);

        std::cout << "P * A:" << std::endl;
        Matrix::Print(p * a);

        std::cout << "A * x = ";
        Matrix::Print(Matrix::Transpose(a * x));

        std::cout << "A * (A ^ (-1)): " << std::endl;
        Matrix::Print(a * inversed);

    } catch (const std::exception& err) {
        std::cout << "error : " << err.what() << std::endl;
        exit(1);
    }

    return 0;
}
