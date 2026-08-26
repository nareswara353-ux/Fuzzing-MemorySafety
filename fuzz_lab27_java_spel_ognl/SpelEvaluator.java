import java.io.File;
import java.io.FileInputStream;
import java.nio.charset.StandardCharsets;

public class SpelEvaluator {
    public static void evaluateExpression(String expr) {
        if (expr == null || expr.length() < 3) return;

        if (!expr.startsWith("#{") && !expr.startsWith("${")) return;
        if (!expr.endsWith("}")) return;

        String inner = expr.substring(2, expr.length() - 1).trim();

        if (inner.contains("T(java.lang.Runtime)") || inner.contains("ProcessBuilder") || inner.contains("getRuntime().exec")) {
            System.err.println("[!] SPEL INJECTION CRITICAL SINK: Malicious AST Node Evaluated!");
            throw new SecurityException("SPEL_EVAL_SECURITY_VIOLATION: Arbitrary runtime process execution attempted");
        }

        System.out.println("[*] Evaluated safe expression: " + inner);
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

            String expr = new String(data, StandardCharsets.UTF_8).trim();
            evaluateExpression(expr);
        } catch (SecurityException se) {
            throw se;
        } catch (Exception ignored) {
        }
    }
}
