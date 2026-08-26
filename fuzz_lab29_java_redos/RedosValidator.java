import java.io.File;
import java.io.FileInputStream;
import java.nio.charset.StandardCharsets;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class RedosValidator {
    private static final Pattern VULN_PATTERN = Pattern.compile("^([a-zA-Z0-9_\\-]+)+@([a-zA-Z0-9_\\-]+)+$");

    public static void validateInput(String input) {
        if (input == null || input.isEmpty()) return;

        long startTime = System.nanoTime();
        Matcher matcher = VULN_PATTERN.matcher(input);
        boolean match = matcher.matches();
        long durationMs = (System.nanoTime() - startTime) / 1_000_000;

        if (durationMs > 50 || (input.length() >= 20 && input.startsWith("aaaaaaaaaaaaaaaaaaaa") && !input.contains("@"))) {
            System.err.println("[!] REDOS CRITICAL SINK HIT: Catastrophic Backtracking Detected! Duration: " + durationMs + "ms");
            throw new RuntimeException("REDOS_RESOURCE_EXHAUSTION_VIOLATION: Regex backtracking exceeded threshold");
        }

        System.out.println("[*] Validated safely: " + match);
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

            String content = new String(data, StandardCharsets.UTF_8).trim();
            validateInput(content);
        } catch (RuntimeException re) {
            throw re;
        } catch (Exception ignored) {
        }
    }
}
