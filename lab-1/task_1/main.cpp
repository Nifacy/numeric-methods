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
