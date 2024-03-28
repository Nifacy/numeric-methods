from math import log


def iterations_method(x0, phi, q, eps, iterations):
    last_x = x0
    i = 0

    while i <= iterations:
        x = phi(last_x)
        if abs(x - last_x) <= (1 - q) / q * eps:
            return x
        last_x = x
        i += 1
    return last_x


def newton_method(x0, f, df, eps, iterations):
    last_x = x0
    i = 0

    while i <= iterations:
        x = last_x - f(last_x) / df(last_x)
        if abs(x - last_x) <= eps:
            return x
        last_x = x
        i += 1
    
    return last_x


f = lambda x: 2 ** x + x ** 2 - 2.0
df = lambda x: log(2) * (2 ** x) + 2.0 * x
phi = lambda x: x - (1.0 / df(1.0)) * f(x)
dphi = lambda x: 1.0 - (1.0 / df(1.0)) * df(x)

print(iterations_method(0.8, phi, dphi(0.0), 0.0001, 100))
print(newton_method(0.8, f, df, 0.0001, 100))
