import time
import statistics
import sys
import tracemalloc

def load_matrices(filename):
    with open(filename, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    n = int(lines[0])

    A = [list(map(float, lines[i].split())) for i in range(1, n + 1)]
    B = [list(map(float, lines[i].split())) for i in range(n + 1, 2 * n + 1)]

    return n, A, B


def multiply(n, A, B):
    C = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            acc = 0.0
            for k in range(n):
                acc += A[i][k] * B[k][j]
            C[i][j] = acc
    return C


def check_correctness():
    A = [[1, 2], [3, 4]]
    B = [[2, 0], [1, 2]]
    expected = [[4, 4], [10, 8]]

    result = multiply(2, A, B)

    if result != expected:
        raise ValueError("Validation error")

    print("Successful validation with a 2x2 matrix.")


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "data/matrix_3.txt"
    n, A, B = load_matrices(filename)

    # Validación
    check_correctness()

    # Warm-up
    _ = multiply(n, A, B)

    # Benchmark
    reps = 5
    times = []

    tracemalloc.start()

    print(f"Benchmark Python ({n}x{n}) ")
    for r in range(reps):
        start = time.perf_counter()
        _ = multiply(n, A, B)
        end = time.perf_counter()

        ms = (end - start) * 1000
        times.append(ms)
        print(f"Repetición {r + 1}: {ms:.4f} ms")

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    mem_mb = peak / (1024 * 1024)

    median = statistics.median(times)
    stddev = statistics.stdev(times) if len(times) > 1 else 0.0

    print("\n Results")
    print(f"Median: {median:.4f} ms")
    print(f"Standard deviation: {stddev:.4f} ms")
    print(f"Peak memory: {mem_mb:.4f} MB")
