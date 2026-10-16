#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include <math.h>
#include <psapi.h>

void multiply(int n, double **A, double **B, double **C) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            double acc = 0.0;
            for (int k = 0; k < n; k++) {
                acc += A[i][k] * B[k][j];
            }
            C[i][j] = acc;
        }
    }
}

void check_correctness() {
    double A_data[2][2] = {{1, 2}, {3, 4}};
    double B_data[2][2] = {{2, 0}, {1, 2}};
    double expected[2][2] = {{4, 4}, {10, 8}};
    double *A[2], *B[2], *C[2];

    for (int i = 0; i < 2; i++) {
        A[i] = A_data[i];
        B[i] = B_data[i];
        C[i] = malloc(2 * sizeof(double));
    }

    multiply(2, A, B, C);

    for (int i = 0; i < 2; i++)
        for (int j = 0; j < 2; j++)
            if (fabs(C[i][j] - expected[i][j]) > 1e-6) {
                printf("Error en la validación.\n");
                exit(1);
            }

    printf("Validación correcta con matriz 2x2.\n");

    for (int i = 0; i < 2; i++) free(C[i]);
}

int cmp_double(const void *a, const void *b) {
    double x = *(double *)a;
    double y = *(double *)b;
    return (x > y) - (x < y);
}

int main(int argc, char *argv[]) {

    const char *filename = (argc > 1) ? argv[1] : "data/matrix_3.txt";

    FILE *f = fopen(filename, "r");
    if (!f) {
        printf("No se pudo abrir el archivo %s\n", filename);
        return 1;
    }

    int n;
    fscanf(f, "%d", &n);

    double **A = malloc(n * sizeof(double *));
    double **B = malloc(n * sizeof(double *));
    double **C = malloc(n * sizeof(double *));
    for (int i = 0; i < n; i++) {
        A[i] = malloc(n * sizeof(double));
        B[i] = malloc(n * sizeof(double));
        C[i] = malloc(n * sizeof(double));
    }

    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            fscanf(f, "%lf", &A[i][j]);

    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            fscanf(f, "%lf", &B[i][j]);

    fclose(f);

    check_correctness();

    multiply(n, A, B, C);

    int reps = 5;
    double times[5];
    LARGE_INTEGER freq, start, end;
    QueryPerformanceFrequency(&freq);

    printf("--- Benchmark C (%dx%d) ---\n", n, n);

    double sum = 0.0;

    for (int r = 0; r < reps; r++) {
        QueryPerformanceCounter(&start);
        multiply(n, A, B, C);
        QueryPerformanceCounter(&end);

        double ms = (double)(end.QuadPart - start.QuadPart) * 1000.0 / freq.QuadPart;
        times[r] = ms;
        sum += ms;

        printf("Repetición %d: %.4f ms\n", r + 1, ms);
    }

    PROCESS_MEMORY_COUNTERS pmc;
    double mem_mb = 0.0;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc))) {
        mem_mb = pmc.PeakWorkingSetSize / (1024.0 * 1024.0);
    }

    double mean = sum / reps;
    double var = 0.0;

    for (int i = 0; i < reps; i++)
        var += pow(times[i] - mean, 2);

    double stddev = sqrt(var / reps);

    qsort(times, reps, sizeof(double), cmp_double);
    double median = times[reps / 2];

    printf("\n--- Resultados ---\n");
    printf("Mediana: %.4f ms\n", median);
    printf("Desviación estándar: %.4f ms\n", stddev);
    printf("Memoria pico: %.4f MB\n", mem_mb);

    for (int i = 0; i < n; i++) {
        free(A[i]);
        free(B[i]);
        free(C[i]);
    }
    free(A);
    free(B);
    free(C);

    return 0;
}
