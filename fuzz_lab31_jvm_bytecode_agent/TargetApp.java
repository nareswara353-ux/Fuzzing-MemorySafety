import java.io.File;
import java.io.FileInputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class TargetApp {
    public static void evaluate(byte[] data) {
        if (data == null || data.length < 8) return;
        CoverageAgent.recordBranch(10);

        ByteBuffer bb = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN);
        int magic = bb.getInt();
        if (magic != 0x41474e54) return;
        CoverageAgent.recordBranch(20);

        int opcode = bb.getInt();
        if (opcode == 0x01) {
            CoverageAgent.recordBranch(30);
        } else if (opcode == 0x77) {
            CoverageAgent.recordBranch(40);
            if (data.length >= 12 && data[8] == 'Z') {
                CoverageAgent.recordBranch(50);
                System.err.println("[!] JVM AGENT TARGET CRASH HIT");
                throw new RuntimeException("JVM_BRANCH_TARGET_CRASH_SINK");
            }
        }
    }

    public static void main(String[] args) {
        if (args.length < 1) return;
        try {
            File f = new File(args[0]);
            if (!f.exists() || f.length() == 0 || f.length() > 4096) return;

            FileInputStream fis = new FileInputStream(f);
            byte[] data = new byte[(int) f.length()];
            fis.read(data);
            fis.close();

            evaluate(data);
        } catch (RuntimeException re) {
            throw re;
        } catch (Exception ignored) {
        } finally {
            CoverageAgent.dumpCoverage("/tmp/jvm_coverage.bin");
        }
    }
}
