#include <iomanip>
#include <iostream>
#include <vector>
#include <stdexcept>


void ReadCoefficients(int step, int n, std::vector<float>& coefs) {
    if (step == 0) {
        coefs[0] = 0.0;
        std::cin >> coefs[1] >> coefs[2] >> coefs[3];
    }

    else if (step == n - 1) {
        coefs[2] = 0.0;
        std::cin >> coefs[0] >> coefs[1] >> coefs[3];
    }

    else {
        std::cin >> coefs[0] >> coefs[1] >> coefs[2] >> coefs[3];
    }
}


void CheckCoefficients(const std::vector<float>& coefs) {
    bool allZero = true;

    for (int i = 0; i < 3; ++i) {
        allZero = allZero && (coefs[i] == 0.0);
    }

    if (allZero && coefs[3] != 0.0) {
        throw std::runtime_error("Can't find solution of system");
    }
}


std::vector<std::vector<float>> ReadRunCoefficients(int n) {
    std::vector<float> coefs(4, 0.0);
    std::vector<std::vector<float>> runCoefs(n, std::vector<float>(2, 0.0));

    for (int i = 0; i < n; ++i) {
        ReadCoefficients(i, n, coefs);
        CheckCoefficients(coefs);

        if (i == 0) {
            if (coefs[1] == 0.0) {
                throw std::runtime_error("Can't find solution of system");
            }

            runCoefs[i][0] = - coefs[2] / coefs[1];
            runCoefs[i][1] = coefs[3] / coefs[1];
        } else {
            float t = coefs[1] + coefs[0] * runCoefs[i - 1][0];

            if (t == 0.0) {
                throw std::runtime_error("Can't find solution of system");
            }

            runCoefs[i][0] = - coefs[2] / t;
            runCoefs[i][1] = (coefs[3] - coefs[0] * runCoefs[i - 1][1]) / t;
        }
    }

    return runCoefs;
}


std::vector<float> Solve(const std::vector<std::vector<float>>& runCoefs) {
    int n = runCoefs.size();
    std::vector<float> x(n, 0.0);

    x[n - 1] = runCoefs[n - 1][1];
    for (int i = n - 2; i >= 0; --i) {
        x[i] = runCoefs[i][0] * x[i + 1] + runCoefs[i][1];
    }

    return x;
}


int ReadNumberOfEquations() {
    int n;
    std::cin >> n;

    if (n <= 0) {
        throw std::runtime_error("number can't be zero o negative");
    }

    return n;
}


void PrintVector(const std::vector<float>& x) {
    std::cout << "[ ";
    for (const float el: x) {
        std::cout << std::setprecision(3) << el << " ";
    }
    std::cout << "]" << std::endl;
}


int main() {
    try {
        int n = ReadNumberOfEquations();
        std::vector<std::vector<float>> runCoefs = ReadRunCoefficients(n);
        std::vector<float> x = Solve(runCoefs);

        std::cout << "x = ";
        PrintVector(x);
        std::cout << std::endl;
    
    } catch(const std::exception& err) {
        std::cout << "error : " << err.what() << std::endl;
        exit(1);
    }

    return 0;
}
