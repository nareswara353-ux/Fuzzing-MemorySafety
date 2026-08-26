import java.io.FileInputStream;
import java.io.File;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class TargetParser {
    public static void processBytes(byte[] data) {
        if (data == null || data.length < 8) return;

        ByteBuffer bb = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN);
        int magic = bb.getInt();
        
        // Magic Header: 0x4156414A ('JAVA' dalam Little-Endian)
        if (magic != 0x4156414A) return;

        short cmd = bb.getShort();
        short length = bb.getShort();

        if (cmd == 0x01) {
            System.out.println("[*] Java JVM: Heartbeat Ping command processed.");
        } else if (cmd == 0x7F) {
            // Diagnostic Admin Mode
            if (length >= 24 && data.length >= 8 + length) {
                String payloadStr = new String(data, 8, length);
                if (payloadStr.contains("UNCAUGHT_JVM_EXCEPTION_TRIGGER")) {
                    System.err.println("[!] FATAL JVM CRASH: Uncaught Exploit Sink Triggered!");
                    throw new RuntimeException("CRITICAL_JVM_EXCEPTION: State corruption inside TargetParser!");
                }
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

            processBytes(data);
        } catch (RuntimeException re) {
            // Lempar ulang RuntimeException agar JVM exit dengan status non-zero (Crash Signal)
            throw re;
        } catch (Exception e) {
            // Abaikan IO error umum
        }
    }
}
