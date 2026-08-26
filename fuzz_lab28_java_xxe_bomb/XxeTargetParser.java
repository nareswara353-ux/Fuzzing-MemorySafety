import java.io.File;
import java.io.FileInputStream;
import java.nio.charset.StandardCharsets;

public class XxeTargetParser {
    public static void parseXmlDocument(String xmlContent) {
        if (xmlContent == null || xmlContent.length() < 10) return;

        if (!xmlContent.contains("<") || !xmlContent.contains(">")) return;

        if (xmlContent.contains("<!DOCTYPE") && xmlContent.contains("<!ENTITY")) {
            if (xmlContent.contains("SYSTEM") || xmlContent.contains("file://") || xmlContent.contains("&lol") || xmlContent.contains("XXE_ENTITY_TRIGGER")) {
                System.err.println("[!] XXE CRITICAL SINK HIT: Malicious Entity Resolution Detected!");
                throw new SecurityException("XXE_CRITICAL_RESOURCE_EXHAUSTION: External entity or recursive expansion attempt");
            }
        }

        System.out.println("[*] XML parsed safely without entity expansion.");
    }

    public static void main(String[] args) {
        if (args.length < 1) return;
        try {
            File f = new File(args[0]);
            if (!f.exists() || f.length() == 0 || f.length() > 8192) return;

            FileInputStream fis = new FileInputStream(f);
            byte[] data = new byte[(int) f.length()];
            fis.read(data);
            fis.close();

            String content = new String(data, StandardCharsets.UTF_8);
            parseXmlDocument(content);
        } catch (SecurityException se) {
            throw se;
        } catch (Exception ignored) {
        }
    }
}
