import sys
import random

def write_matrix(n, file):
    for _ in range(n):
        row = [str(float(random.randint(1, 10))) for _ in range(n)]
        file.write(" ".join(row) + "\n")

def create_input_file(n, filename):
    with open(filename, "w") as f:
        f.write(f"{n}\n")
        write_matrix(n, f)  # Matrix A
        write_matrix(n, f)  # Matrix B

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    filename = sys.argv[2] if len(sys.argv) > 2 else f"data/matrix_{n}.txt"

    create_input_file(n, filename)
    print(f" '{filename}' file generated correctly ({n}x{n}).")
