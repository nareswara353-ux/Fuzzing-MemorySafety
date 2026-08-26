import java.io.File;
import java.io.FileInputStream;

public class VulnArrayHandler {
    public static void process(byte[] data) {
        if (data == null) return;
        byte[] buffer = new byte[16];
        int limit = data.length;
        for (int i = 0; i < limit; i++) {
            buffer[i] = data[i];
        }
        System.out.println("[*] Processed successfully: " + data.length);
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

            process(data);
        } catch (RuntimeException re) {
            throw re;
        } catch (Exception ignored) {
        }
    }
}
