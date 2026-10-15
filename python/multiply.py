import time
import argparse
import json
import platform
import sys

def matrices(n):
    a = [[(((i * 17 + j * 13 + 7) % 101) - 50) / 50.0 for j in range(n)] for i in range(n)]
    b = [[(((i * 11 + j * 19 + 23) % 101) - 50) / 50.0 for j in range(n)] for i in range(n)]
    return a, b

def multiply(a, b):
    n = len(a)
    c = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = 0.0
            for k in range(n):
                s += a[i][k] * b[k][j]
            c[i][j] = s
    return c

def checksum(c):
    n = len(c)
    return sum(c[i][j] * (1 + ((i * 7 + j * 3) % 11)) for i in range(n) for j in range(n))

def known_tests():
    a = [[1.0, 2.0], [3.0, 4.0]]
    b = [[5.0, 6.0], [7.0, 8.0]]
    expected = [[19.0, 22.0], [43.0, 50.0]]
    assert multiply(a, b) == expected
    ident = [[1.0, 0.0], [0.0, 1.0]]
    zero = [[0.0, 0.0], [0.0, 0.0]]
    assert multiply(a, ident) == a
    assert multiply(a, zero) == zero

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--repetitions", type=int, default=5)
    p.add_argument("--warmups", type=int, default=2)
    args = p.parse_args()
    known_tests()
    a, b = matrices(args.n)
    for _ in range(args.warmups):
        c = multiply(a, b)
        check = checksum(c)
    times, check = [], 0.0
    for _ in range(args.repetitions):
        start = time.perf_counter()
        c = multiply(a, b)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        check = checksum(c)
    print(json.dumps({"language":"Python", "n":args.n, "times_seconds":times, "checksum":check,
                      "python":sys.version.split()[0], "implementation":platform.python_implementation()}))

if __name__ == "__main__":
    main()
