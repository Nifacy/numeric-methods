#ifndef MATRIX_H
#define MATRIX_H

#include <iostream>
#include <iomanip>
#include <vector>

namespace Matrix {

    using TSize = std::tuple<int, int>;

    class TMatrix {
    public:
        TMatrix(const TMatrix& m)
            : _data(m._data),
              _size(m._size)
        { }

        TMatrix(int n, int m)
            : _data(n * m, 0.0),
              _size{n, m}
        { }

        static TMatrix Eye(int n) {
            TMatrix matrix(n, n);

            for (int i = 0; i < n; ++i) {
                matrix.Set(i, i, 1.0);
            }

            return matrix;
        }

        float Get(int i, int j) const {
            return this->_data[i * std::get<1>(this->_size) + j];
        }

        void Set(int i, int j, float value) {
            this->_data[i * std::get<1>(this->_size) + j] = value;
        }

        void Swap(int i, int j) {
            int n = std::get<1>(GetSize());
            float temp;

            for (int t = 0; t < n; ++t) {
                temp = Get(i, t);
                Set(i, t, Get(j, t));
                Set(j, t, temp);
            }
        }

        TSize GetSize() const {
            return this->_size;
        }

        TMatrix& operator=(const TMatrix& other) {
            this->_data = other._data;
            this->_size = other._size;
            return *this;
        }

    private:
        std::vector<float> _data;
        TSize _size;
    };

    void Print(const Matrix::TMatrix& m) {
        int a = std::get<0>(m.GetSize());
        int b = std::get<1>(m.GetSize());
        std::cout << std::fixed;

        for (int i = 0; i < a; ++i) {
            for (int j = 0; j < b; ++j) {
                float elem = m.Get(i, j);
                char sign = (elem >= 0.0) ? ' ' : '-';

                if (elem < 0.0) {
                    elem *= -1.0;
                }

                std::cout << std::setprecision(3) << sign << elem << " ";
            }
            std::cout << "\n";
        }
    }

    void Read(Matrix::TMatrix& m) {
        int w = std::get<0>(m.GetSize());
        int h = std::get<1>(m.GetSize());
        float element;

        for (int i = 0; i < w; ++i) {
            for (int j = 0; j < h; ++j) {
                std::cin >> element;
                m.Set(i, j, element);
            }
        }
    }

}

#endif // MATRIX_H
