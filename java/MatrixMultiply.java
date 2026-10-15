import java.util.Arrays;

public class MatrixMultiply {
    static double[][] matricesA(int n) {
        double[][] a = new double[n][n];
        for (int i=0;i<n;i++) for (int j=0;j<n;j++)
            a[i][j] = (((i*17 + j*13 + 7) % 101) - 50) / 50.0;
        return a;
    }
    static double[][] matricesB(int n) {
        double[][] b = new double[n][n];
        for (int i=0;i<n;i++) for (int j=0;j<n;j++)
            b[i][j] = (((i*11 + j*19 + 23) % 101) - 50) / 50.0;
        return b;
    }
    static double[][] multiply(double[][] a, double[][] b) {
        int n=a.length;
        double[][] c=new double[n][n];
        for (int i=0;i<n;i++) for (int j=0;j<n;j++) {
            double s=0.0;
            for (int k=0;k<n;k++) s += a[i][k]*b[k][j];
            c[i][j]=s;
        }
        return c;
    }
    static double checksum(double[][] c) {
        int n=c.length; double sum=0.0;
        for (int i=0;i<n;i++) for (int j=0;j<n;j++) sum += c[i][j]*(1+((i*7+j*3)%11));
        return sum;
    }
    static void knownTests() {
        double[][] a={{1,2},{3,4}}, b={{5,6},{7,8}};
        double[][] expected={{19,22},{43,50}};
        double[][] c=multiply(a,b);
        for(int i=0;i<2;i++) for(int j=0;j<2;j++)
            if(Math.abs(c[i][j]-expected[i][j])>1e-12) throw new AssertionError("known test failed");
        double[][] id={{1,0},{0,1}}, zero={{0,0},{0,0}};
        if(Math.abs(multiply(a,id)[1][1]-4)>1e-12 || Math.abs(checksum(multiply(a,zero)))>1e-12)
            throw new AssertionError("identity/zero test failed");
    }
    public static void main(String[] args) {
        int n=Integer.parseInt(args[0]), repetitions=Integer.parseInt(args[1]), warmups=Integer.parseInt(args[2]);
        knownTests();
        double[][] a=matricesA(n), b=matricesB(n);
        for(int i=0;i<warmups;i++) checksum(multiply(a,b));
        double[] times=new double[repetitions]; double check=0.0;
        for(int i=0;i<repetitions;i++) {
            long start=System.nanoTime();
            double[][] c=multiply(a,b);
            times[i]=(System.nanoTime()-start)/1e9;
            check=checksum(c);
        }
        System.out.print("{\"language\":\"Java\",\"n\":"+n+",\"times_seconds\":[");
        for(int i=0;i<times.length;i++){ if(i>0)System.out.print(","); System.out.print(times[i]); }
        System.out.println("],\"checksum\":"+check+",\"java\":\""+System.getProperty("java.version")+"\"}");
    }
}
