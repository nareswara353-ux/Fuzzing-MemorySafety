import java.io.File;
import java.io.FileInputStream;
import java.io.DataInputStream;
import java.io.ByteArrayInputStream;

public class InsecureDeserializer {
    public static final short STREAM_MAGIC = (short) 0xaced;
    public static final short STREAM_VERSION = 5;

    public static void deserializePayload(byte[] rawData) throws Exception {
        if (rawData == null || rawData.length < 8) return;

        DataInputStream dis = new DataInputStream(new ByteArrayInputStream(rawData));
        
        // Layer 1: Validasi Header Stream Java (0xACED 0x0005)
        short magic = dis.readShort();
        short version = dis.readShort();
        if (magic != STREAM_MAGIC || version != STREAM_VERSION) return;

        // Layer 2: Baca Type Code
        byte tc = dis.readByte();
        if (tc != (byte) 0x73) return; // TC_OBJECT

        byte tcClass = dis.readByte();
        if (tcClass != (byte) 0x72) return; // TC_CLASSDESC

        // Layer 3: Baca Nama Kelas (UTF String)
        int classNameLen = dis.readUnsignedShort();
        if (classNameLen <= 0 || classNameLen > 128 || dis.available() < classNameLen) return;

        byte[] nameBytes = new byte[classNameLen];
        dis.readFully(nameBytes);
        String className = new String(nameBytes, "UTF-8");

        // SECURITY SINK: Deteksi Insecure Gadget Class Injection
        if (className.equals("org.vulnerable.GadgetPayload") || className.contains("EXPLOIT_GADGET_TRIGGER")) {
            System.err.println("[!] DESERIALIZATION SECURITY SINK HIT: Unwhitelisted Gadget Invoked: " + className);
            throw new SecurityException("DESERIALIZATION_CRITICAL_VIOLATION: Arbitrary class instantiation detected -> " + className);
        } else {
            System.out.println("[*] Safe object deserialized: " + className);
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

            deserializePayload(data);
        } catch (SecurityException se) {
            // Lempar ulang security violation agar tertangkap oleh fuzzer oracle
            throw se;
        } catch (Exception ignored) {
        }
    }
}
