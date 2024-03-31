from numpy import arange


def derivative(f):
    DX = 0.00001
    return lambda x: (f(x + DX) - f(x)) / DX


def sign(x):
    if x == 0.0: return 0.0
    if x < 0.0: return -1.0
    return 1.0


def iterations_method(f, a, b, eps, iterations):
    x0 = (a + b) / 2.0
    step = 0.001
    df = derivative(f)
    max_df = max(abs(df(x)) for x in arange(a, b, step))
    sign_f = sign(df(a))
    phi = lambda x: x - (sign_f / max_df) * f(x)
    dphi = derivative(phi)
    q = max(abs(dphi(x)) for x in arange(a, b, step))

    last_x = x0
    i = 0

    while i <= iterations:
        x = phi(last_x)
        if abs(x - last_x) <= (1 - q) / q * eps:
            return x
        last_x = x
        i += 1

    return last_x


def newton_method(f, a, b, eps, iterations):
    x0 = (a + b) / 2.0
    last_x = x0
    df = derivative(f)
    i = 0

    while i <= iterations:
        x = last_x - f(last_x) / df(last_x)
        if abs(x - last_x) <= eps:
            return x
        last_x = x
        i += 1
    
    return last_x


if __name__ == '__main__':
    f = lambda x: 2 ** x + x ** 2 - 2.0
    a, b = 0.5, 1.0
    eps = 0.0001
    iterations = 100

    print(iterations_method(f, a, b, eps, iterations))
    print(newton_method(f, a, b, eps, iterations))
