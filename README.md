# Assigment1-Matrix-Multiplication
## Overview.
This project compares the performance of matrix multiplication implemented in Python, Java and C. The objective is to analyse execution time and memory usage for square matrices of increasing sizes.

All implementations use three nested loops and perform five timed repetitions. The median and standard deviation are calculated, and correctness is checked using a 2 × 2 test case.

## Environment details.
The project is designed for Windows.
Record the following specifications from the computer used for the experiments:
Operating system: Windows 11 home, 26H2.
CPU and RAM: Intel(R) Core(TM) Ultra 7 255H (2.00 GHz)/ 16,0 GB (15,4 GB usable)
Python, Java, C: As I mentioned in the email, I currently do not have a functioning computer to complete all the required tasks. I am working on resolving the issue, and in the meantime I have done as much as I could. Once I am able to fix it, I will review and update everything accordingly.

## Programming languajes.
Python: Matrix multiplication, timing and memory allocation measurement.
Java: Matrix multiplication, timing and heap memory measurement.
C: Matrix multiplication, timing and process memory measurement.

## Dependencies.
Python 3 (standard library).
Java Development Kit (JDK).
GCC/MinGW-w64 for C on Windows, with the Windows API library psapi.
No third-party Python packages are required by the supplied scripts.

## Repository Structure.
Assignment01-Matrix-Multiplication/
│
├── README.md
├── evaluation.py 
├── make.py
│
├── data/
│
├── src/
│   ├── python/
│   │   └── multiply.py
│   │
│   ├── java/
│   │   └── MultiplySimple.java
│   │
│   └── c/
│       └── matrix_multiply.c
│
└── results.md


evaluation.py: Runs the benchmarks and summarizes the results.
make.py: Generates input matrices.
data/: Stores matrix input files.
src/: Contains the implementations in the three languages.
results.md: Stores the benchmark summary.

## Execution Instructions.
Run these commands from the project root in PowerShell.
#### Step 1. Generate matrices
mkdir data
python make.py 3 data/matrix_3.txt

#### Step 2. Run Python
python src/python/multiply.py data/matrix_3.txt

#### Step 3. Compile and run Java
javac src/java/MultiplySimple.java
java -cp src/java MultiplySimple data/matrix_3.txt

#### Step 4. Compile and run C
gcc src/c/matrix_multiply.c -o src/c/matrix_multiply.exe -lpsapi -lm
src/c/matrix_multiply.exe data/matrix_3.txt

#### Step 5. Run the evaluation
python evaluation.py
