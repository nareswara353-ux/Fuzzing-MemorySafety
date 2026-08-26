import java.io.File;
import java.io.FileInputStream;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

public class JwtAuthService {
    public static void verifyAndAuthenticate(String token) {
        if (token == null || !token.contains(".")) return;

        String[] parts = token.split("\\.");
        if (parts.length < 2) return;

        try {
            String headerJson = new String(Base64.getUrlDecoder().decode(parts[0]), StandardCharsets.UTF_8);
            String payloadJson = new String(Base64.getUrlDecoder().decode(parts[1]), StandardCharsets.UTF_8);

            String sig = (parts.length == 3) ? parts[2] : "";

            if (headerJson.toLowerCase().contains("\"alg\":\"none\"") || headerJson.toLowerCase().contains("\"alg\": \"none\"")) {
                if (payloadJson.contains("\"role\":\"admin\"") || payloadJson.contains("\"admin\":true")) {
                    System.err.println("[!] JWT SECURITY SINK HIT: None-algorithm signature bypass accepted for admin role!");
                    throw new SecurityException("JWT_SIGNATURE_BYPASS_DETECTED: Insecure None algorithm accepted");
                }
            }

            if (sig.isEmpty() && payloadJson.contains("\"role\":\"admin\"")) {
                System.err.println("[!] JWT SECURITY SINK HIT: Empty signature accepted!");
                throw new SecurityException("JWT_SIGNATURE_BYPASS_DETECTED: Missing signature verification");
            }

            System.out.println("[*] Processed token safely: " + payloadJson);
        } catch (IllegalArgumentException ignored) {
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

            String token = new String(data, StandardCharsets.UTF_8).trim();
            verifyAndAuthenticate(token);
        } catch (SecurityException se) {
            throw se;
        } catch (Exception ignored) {
        }
    }
}
