#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

static double **alloc_matrix(int n) {
    double **m = malloc((size_t)n * sizeof(*m));
    if (!m) { perror("malloc"); exit(2); }
    for (int i=0;i<n;i++) {
        m[i] = calloc((size_t)n, sizeof(**m));
        if (!m[i]) { perror("calloc"); exit(2); }
    }
    return m;
}
static void free_matrix(double **m, int n) { for(int i=0;i<n;i++) free(m[i]); free(m); }
static void fill(double **a, double **b, int n) {
    for(int i=0;i<n;i++) for(int j=0;j<n;j++) {
        a[i][j] = (((i*17 + j*13 + 7) % 101) - 50) / 50.0;
        b[i][j] = (((i*11 + j*19 + 23) % 101) - 50) / 50.0;
    }
}
static double **multiply(double **a, double **b, int n) {
    double **c=alloc_matrix(n);
    for(int i=0;i<n;i++) for(int j=0;j<n;j++) {
        double s=0.0;
        for(int k=0;k<n;k++) s += a[i][k]*b[k][j];
        c[i][j]=s;
    }
    return c;
}
static double checksum(double **c, int n) {
    double sum=0.0;
    for(int i=0;i<n;i++) for(int j=0;j<n;j++) sum += c[i][j]*(1+((i*7+j*3)%11));
    return sum;
}
static double now_seconds(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (double)t.tv_sec + (double)t.tv_nsec / 1e9;
}
static void known_tests(void) {
    double **a=alloc_matrix(2), **b=alloc_matrix(2);
    a[0][0]=1; a[0][1]=2; a[1][0]=3; a[1][1]=4;
    b[0][0]=5; b[0][1]=6; b[1][0]=7; b[1][1]=8;
    double **c=multiply(a,b,2);
    double expected[2][2]={{19,22},{43,50}};
    for(int i=0;i<2;i++) for(int j=0;j<2;j++)
        if(fabs(c[i][j]-expected[i][j])>1e-12) { fprintf(stderr,"known test failed\n"); exit(3); }
    free_matrix(a,2); free_matrix(b,2); free_matrix(c,2);
}
int main(int argc, char **argv) {
    if(argc!=4) { fprintf(stderr,"usage: matrix_multiply n repetitions warmups\n"); return 1; }
    int n=atoi(argv[1]), reps=atoi(argv[2]), warmups=atoi(argv[3]);
    if(n<1 || reps<1 || warmups<0) return 1;
    known_tests();
    double **a=alloc_matrix(n), **b=alloc_matrix(n);
    fill(a,b,n);
    for(int i=0;i<warmups;i++) { double **c=multiply(a,b,n); volatile double check=checksum(c,n); (void)check; free_matrix(c,n); }
    printf("{\"language\":\"C\",\"n\":%d,\"times_seconds\":[",n);
    double check=0.0;
    for(int i=0;i<reps;i++) {
        double start=now_seconds();
        double **c=multiply(a,b,n);
        double elapsed=now_seconds()-start;
        check=checksum(c,n);
        free_matrix(c,n);
        if(i) printf(",");
        printf("%.9f",elapsed);
    }
    printf("],\"checksum\":%.12f}\n",check);
    free_matrix(a,n); free_matrix(b,n);
    return 0;
}
