import java.io.FileOutputStream;
import java.io.File;

public class CoverageAgent {
    public static final byte[] coverageMap = new byte[65536];

    public static void recordBranch(int branchId) {
        coverageMap[branchId & 0xFFFF]++;
    }

    public static void dumpCoverage(String filePath) {
        try {
            FileOutputStream fos = new FileOutputStream(new File(filePath));
            fos.write(coverageMap);
            fos.close();
        } catch (Exception ignored) {
        }
    }
}
