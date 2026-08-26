import java.io.File;
import java.io.FileInputStream;

public class NativeBridge {
    static {
        System.loadLibrary("native_engine");
    }

    public native void processNative(byte[] data, int len);

    public static void main(String[] args) {
        if (args.length < 1) return;
        try {
            File f = new File(args[0]);
            if (!f.exists() || f.length() == 0 || f.length() > 4096) return;

            FileInputStream fis = new FileInputStream(f);
            byte[] data = new byte[(int) f.length()];
            fis.read(data);
            fis.close();

            NativeBridge bridge = new NativeBridge();
            bridge.processNative(data, data.length);
        } catch (Exception ignored) {
        }
    }
}
