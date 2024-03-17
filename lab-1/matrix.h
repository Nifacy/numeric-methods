#ifndef MATRIX_H
#define MATRIX_H

#include <iostream>
#include <iomanip>
#include <vector>

namespace Matrix {

    using TSize = std::pair<int, int>;

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

        TMatrix(const std::vector<std::vector<float>>& data)
            : TMatrix(data.size(), data[0].size())
        {
            for (int i = 0; i < data.size(); ++i) {
                for (int j = 0; j < data[0].size(); ++j) {
                    Set(i, j, data[i][j]);
                }
            }
        }

        static TMatrix Eye(int n) {
            TMatrix matrix(n, n);

            for (int i = 0; i < n; ++i) {
                matrix.Set(i, i, 1.0);
            }

            return matrix;
        }

        float Get(int i, int j) const {
            return this->_data[i * this->_size.second + j];
        }

        void Set(int i, int j, float value) {
            this->_data[i * this->_size.second + j] = value;
        }

        void SwapRaws(int i, int j) {
            int n = GetSize().second;
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

    /* Operations */

    void Add(const TMatrix& a, const TMatrix& b, TMatrix& res) {
        int n = a.GetSize().first;
        int m = a.GetSize().second;

        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < m; ++j) {
                res.Set(i, j, a.Get(i, j) + b.Get(i, j));
            }
        }
    }

    TMatrix Add(const TMatrix& a, const TMatrix& b) {
        int n = a.GetSize().first;
        int m = a.GetSize().second;

        TMatrix res(n, m);
        Add(a, b, res);
        return res;
    }

    void Mult(const TMatrix& a, const TMatrix& b, TMatrix& res) {
        int n = a.GetSize().first;
        int p = a.GetSize().second;
        int m = b.GetSize().second;
        float acc;

        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < m; ++j) {
                acc = 0.0;

                for (int t = 0; t < p; ++t) {
                    acc += a.Get(i, t) * b.Get(t, j);
                }

                res.Set(i, j, acc);
            }
        }
    }

    TMatrix Mult(const TMatrix& a, const TMatrix& b) {
        int n = a.GetSize().first;
        int m = b.GetSize().second;

        TMatrix res(n, m);
        Mult(a, b, res);
        return res;
    }

    void Mult(const TMatrix& a, float k, TMatrix& res) {
        int n = a.GetSize().first;
        int m = a.GetSize().second;

        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < m; ++j) {
                res.Set(i, j, a.Get(i, j) * k);
            }
        }
    }

    TMatrix Mult(const TMatrix& a, float k) {
        int n = a.GetSize().first;
        int m = a.GetSize().second;

        TMatrix res(n, m);
        Mult(a, k, res);
        return res;
    }

    TMatrix Transpose(const TMatrix& a) {
        int n = a.GetSize().first;
        int m = a.GetSize().second;

        TMatrix res(m, n);

        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < m; ++j) {
                res.Set(j, i, a.Get(i, j));
            }
        }

        return res;
    }

    /* IO Functions */

    void Print(const TMatrix& m) {
        int a = m.GetSize().first;
        int b = m.GetSize().second;
        std::cout << std::fixed;

        for (int i = 0; i < a; ++i) {
            for (int j = 0; j < b; ++j) {
                float elem = m.Get(i, j);
                char sign = (elem >= 0.0) ? ' ' : '-';

                if (elem < 0.0) {
                    elem *= -1.0;
                }

                std::cout << std::setprecision(6) << sign << elem << " ";
            }
            std::cout << "\n";
        }
    }

    void Read(TMatrix& m) {
        int w = m.GetSize().first;
        int h = m.GetSize().second;
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
