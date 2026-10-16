import os
import subprocess
import re

sizes = [10, 50, 100, 250, 500]
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

results = {n: {} for n in sizes}


print("Compilation.")

print("Compiling C...")
c_build = subprocess.run(
    ["gcc", "src/c/multiply.c", "-o", "src/c/multiply.exe", "-lpsapi"],
    capture_output=True, text=True
)
if c_build.returncode != 0:
    print("Error compiling C:", c_build.stderr)

print("Compiling Java...")
java_build = subprocess.run(
    ["javac", "src/java/Multiply.java"],
    capture_output=True, text=True
)
if java_build.returncode != 0:
    print("Error compiling Java:", java_build.stderr)

print("\n Matrix generation.")

for n in sizes:
    path = os.path.join(data_dir, f"matrix_{n}.txt")
    if not os.path.exists(path):
        print(f"Generando {path}...")
        subprocess.run(["python", "src/python/generator.py", str(n), path])


def parse_metrics(text):
    get = lambda pattern: re.search(pattern, text)

    median = get(r"Median:\s*([\d\.]+)")
    stddev = get(r"(?:StdDev|Variability).*:\s*([\d\.]+)")
    memory = get(r"(?:Peak Memory|Heap).*:\s*([\d\.]+)")

    return {
        "median": float(median.group(1)) if median else None,
        "stddev": float(stddev.group(1)) if stddev else None,
        "memory": float(memory.group(1)) if memory else None
    }

def cell(metrics):
    if metrics["median"] is None:
        return "Error | Error"
    return f"{metrics['median']:.4f} ± {metrics['stddev']:.4f} ms | {metrics['memory']:.4f} MB"

print("\n Benchmarks.")

for n in sizes:
    file = os.path.join(data_dir, f"matrix_{n}.txt")
    print(f"\n--- n = {n} ---")

    # Python
    out_py = subprocess.run(
        ["python", "src/python/multiply.py", file],
        capture_output=True, text=True
    ).stdout
    results[n]["Python"] = parse_metrics(out_py)
    print("Python:", results[n]["Python"]["median"], "ms")

    # C
    out_c = subprocess.run(
        ["src/c/multiply.exe", file],
        capture_output=True, text=True
    ).stdout
    results[n]["C"] = parse_metrics(out_c)
    print("C:", results[n]["C"]["median"], "ms")

    # Java
    out_java = subprocess.run(
        ["java", "-cp", "src/java", "Multiply", file],
        capture_output=True, text=True
    ).stdout
    results[n]["Java"] = parse_metrics(out_java)
    print("Java:", results[n]["Java"]["median"], "ms")

print("\n\n Results.")

table = (
    "| n | Python | C | Java |\n"
    "|---|--------|---|------|\n"
)

for n in sizes:
    table += (
        f"| {n}x{n} | "
        f"{cell(results[n]['Python'])} | "
        f"{cell(results[n]['C'])} | "
        f"{cell(results[n]['Java'])} |\n"
    )

print(table)

with open("results.md", "w", encoding="utf-8") as f:
    f.write("# Benchmark Results\n\n")
    f.write("Format: `Median ± Standard Deviation`.\n\n")
    f.write(table)

print("'results.md' file generated successfully.")
