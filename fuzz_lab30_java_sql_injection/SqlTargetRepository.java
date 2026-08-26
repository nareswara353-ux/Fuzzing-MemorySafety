import java.io.File;
import java.io.FileInputStream;
import java.nio.charset.StandardCharsets;

public class SqlTargetRepository {
    public static void executeSearchQuery(String userInput) {
        if (userInput == null || userInput.isEmpty()) return;

        String rawQuery = "SELECT * FROM users WHERE username = '" + userInput + "' AND status = 'ACTIVE'";

        String upper = userInput.toUpperCase();
        if (userInput.contains("'") && (upper.contains("OR ") || upper.contains("UNION ") || upper.contains("--") || upper.contains("1=1"))) {
            System.err.println("[!] SQL INJECTION SINK HIT: Query Syntax Broken -> " + rawQuery);
            throw new SecurityException("SQL_INJECTION_SECURITY_VIOLATION: Malicious SQL fragment parsed into dynamic query");
        }

        System.out.println("[*] Query executed safely: " + rawQuery);
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

            String input = new String(data, StandardCharsets.UTF_8).trim();
            executeSearchQuery(input);
        } catch (SecurityException se) {
            throw se;
        } catch (Exception ignored) {
        }
    }
}
