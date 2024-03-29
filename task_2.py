from math import exp
import numpy as np


def norm(matrix):
    return abs(matrix).max()

def iteration_method(x0, phi, eps, iterations):
    last_x = x0
    i = 0

    while i <= iterations:
        x = phi(last_x)
        if norm(x - last_x) <= eps:
            return x
        last_x = x
        i += 1

    return last_x


def newton_method(x0, f, J, eps, iterations):
    last_x = x0
    i = 0

    while i <= iterations:
        dx = np.linalg.solve(J(last_x), -f(last_x))
        x = last_x + dx

        if norm(x - last_x) <= eps:
            return x
        
        last_x = x
        i += 1
    
    return last_x


x = np.array([1.0, 2.0])

a = 2.0
f1 = lambda x: x[0] ** 2 + x[1] ** 2 - a ** 2
f2 = lambda x: x[0] - exp(x[1]) + a

df1 = lambda x: np.array([2.0 * x[0], 2.0 * x[1]])
df2 = lambda x: np.array([1.0, -exp(x[1])])

phi1 = lambda x: x[0] - (1.0 / norm(df1(np.array([2.0, 2.0])))) * f1(x)
phi2 = lambda x: x[1] - (-1.0 / norm(df2(np.array([2.0, 2.0])))) * f2(x)

phi = lambda x: np.array([phi1(x), phi2(x)])
x0 = np.array([1.5, 1.5])
eps = 0.0001
iterations = 100

f = lambda x: np.array([f1(x), f2(x)])
J = lambda x: np.array([df1(x), df2(x)])

print(iteration_method(x0, phi, eps, iterations))
print(newton_method(x0, f, J, eps, iterations))
