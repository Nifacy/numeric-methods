import numpy as np

from lab_1.task_2 import solve_system


class CubicSplineInterploation:
    def __init__(self, nodes: list[tuple[float, float]]):
        x, f = map(np.array, zip(*nodes))
        h = self._get_h(x)
        self.c = self._get_coef_c(h, f)
        self.a = self._get_coef_a(f)
        self.b = self._get_coef_b(h, self.c, f)
        self.d = self._get_coef_d(h, self.c)
        self.x = x

    def __call__(self, x: float) -> float:
        for i in range(1, len(self.x)):
            if self.x[i - 1] <= x <= self.x[i]:
                h = x - self.x[i - 1]
                return self.a[i] + self.b[i] * h + self.c[i] * h**2 + self.d[i] * h**3
        return np.nan

    @classmethod
    def _get_h(cls, x):
        n = len(x) - 1
        return np.array(
            [0] + [x[i] - x[i - 1] for i in range(1, n + 1)],
            dtype=np.float32,
        )

    @classmethod
    def _get_coef_c(cls, h, f):
        A, B = cls._get_system_coefs(h, f)
        c = np.zeros_like(h)
        c[2:] = solve_system(A, B)
        return c

    @classmethod
    def _get_coef_a(cls, f):
        a = np.zeros_like(f)
        a[1:] = f[:-1]
        return a

    @classmethod
    def _get_coef_b(cls, h, c, f):
        n = len(f) - 1
        b = np.zeros(n + 1)

        for i in range(1, n):
            b[i] = (f[i] - f[i - 1]) / h[i] - (h[i] * (c[i + 1] + 2 * c[i])) / 3.0
        b[n] = (f[n] - f[n - 1]) / h[n] - 2.0 / 3.0 * h[n] * c[n]

        return b

    @classmethod
    def _get_coef_d(cls, h, c):
        n = len(c) - 1
        d = np.zeros(n + 1)

        for i in range(1, n):
            d[i] = (c[i + 1] - c[i]) / (3.0 * h[i])
        d[n] = -c[n] / (3.0 * h[n])
        return d

    @classmethod
    def _get_system_coefs(cls, h, f):
        n = len(f) - 1
        A = np.zeros((n - 1, 3))
        B = np.zeros((n - 1, 1))

        for i in range(2, n + 1):
            a, b, c = h[i - 1], 2 * (h[i - 1] + h[i]), h[i]
            d = 3 * ((f[i] - f[i - 1]) / h[i] - (f[i - 1] - f[i - 2]) / h[i - 1])

            if i == 2:
                A[i - 2, :] = 0, b, c
            elif i == n:
                A[i - 2, :] = a, b, 0
            else:
                A[i - 2, :] = a, b, c
            B[i - 2, 0] = d

        return A, B
