import java.io.File;
import java.io.FileNotFoundException;
import java.util.Locale;
import java.util.Scanner;

public class MultiplySimple {

    public static void multiply(double[][] A, double[][] B, double[][] C, int n) {
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

    public static void checkCorrectness() {
        double[][] A = {{1, 2}, {3, 4}};
        double[][] B = {{2, 0}, {1, 2}};
        double[][] C = new double[2][2];

        double[][] expected = {{4, 4}, {10, 8}};

        multiply(A, B, C, 2);

        for (int i = 0; i < 2; i++) {
            for (int j = 0; j < 2; j++) {
                if (Math.abs(C[i][j] - expected[i][j]) > 1e-6) {
                    System.out.println("Validation error");
                    System.exit(1);
                }
            }
        }
        System.out.println("Successful validation with a 2x2 matrix.");
    }

    public static double[][][] loadMatrices(String filename) {
        try {
            Scanner sc = new Scanner(new File(filename));
            sc.useLocale(Locale.US);

            int n = sc.nextInt();
            double[][] A = new double[n][n];
            double[][] B = new double[n][n];

            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    A[i][j] = sc.nextDouble();

            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    B[i][j] = sc.nextDouble();

            sc.close();
            return new double[][][]{A, B, new double[n][n]};
        } catch (FileNotFoundException e) {
            System.out.println("File not found: " + filename);
            System.exit(1);
        }
        return null;
    }

    public static void main(String[] args) {

        String filename = (args.length > 0) ? args[0] : "data/matrix_3.txt";

        double[][][] matrices = loadMatrices(filename);
        double[][] A = matrices[0];
        double[][] B = matrices[1];
        double[][] C = matrices[2];
        int n = A.length;

        checkCorrectness();

        multiply(A, B, C, n);

        int reps = 5;
        double[] times = new double[reps];
        double total = 0;

        System.out.println("Java Benchmark (" + n + "x" + n + ") ---");

        for (int r = 0; r < reps; r++) {
            long start = System.nanoTime();
            multiply(A, B, C, n);
            long end = System.nanoTime();

            double ms = (end - start) / 1_000_000.0;
            times[r] = ms;
            total += ms;

            System.out.printf(Locale.US, "Repetition %d: %.4f ms\n", r + 1, ms);
        }

        Runtime rt = Runtime.getRuntime();
        rt.gc();
        double usedMB = (rt.totalMemory() - rt.freeMemory()) / (1024.0 * 1024.0);

        double mean = total / reps;

        double var = 0;
        for (double t : times) var += Math.pow(t - mean, 2);
        double stddev = Math.sqrt(var / reps);

        double median = times[reps / 2];

        System.out.println("\nResults:");
        System.out.printf(Locale.US, "Median: %.4f ms\n", median);
        System.out.printf(Locale.US, "Standard deviation: %.4f ms\n", stddev);
        System.out.printf(Locale.US, "Used memory (heap): %.4f MB\n", usedMB);
    }
}
