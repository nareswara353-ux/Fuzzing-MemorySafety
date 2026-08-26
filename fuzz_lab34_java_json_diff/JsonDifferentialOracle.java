import java.io.File;
import java.io.FileInputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

public class JsonDifferentialOracle {
    public static Map<String, String> parseStrict(String json) {
        Map<String, String> map = new HashMap<>();
        if (!json.startsWith("{") || !json.endsWith("}")) return map;
        String body = json.substring(1, json.length() - 1).trim();
        if (body.isEmpty()) return map;

        String[] pairs = body.split(",");
        for (String pair : pairs) {
            String[] kv = pair.split(":");
            if (kv.length != 2) return map;
            String k = kv[0].trim().replace("\"", "");
            String v = kv[1].trim().replace("\"", "");
            if (!map.containsKey(k)) {
                map.put(k, v);
            }
        }
        return map;
    }

    public static Map<String, String> parseLenient(String json) {
        Map<String, String> map = new HashMap<>();
        String sanitized = json.replaceAll("/\\*.*?\\*/", "");
        if (!sanitized.startsWith("{") || !sanitized.endsWith("}")) return map;
        String body = sanitized.substring(1, sanitized.length() - 1).trim();
        if (body.isEmpty()) return map;

        String[] pairs = body.split(",");
        for (String pair : pairs) {
            String[] kv = pair.split(":");
            if (kv.length != 2) return map;
            String k = kv[0].trim().replace("\"", "");
            String v = kv[1].trim().replace("\"", "");
            map.put(k, v);
        }
        return map;
    }

    public static void evaluateDifferential(String json) {
        Map<String, String> strictResult = parseStrict(json);
        Map<String, String> lenientResult = parseLenient(json);

        if (strictResult.isEmpty() && lenientResult.isEmpty()) return;

        if (!strictResult.equals(lenientResult)) {
            System.err.println("[!] DIFFERENTIAL DISCREPANCY DETECTED!");
            System.err.println("Strict: " + strictResult + " vs Lenient: " + lenientResult);
            throw new IllegalStateException("JSON_DIFFERENTIAL_DISCREPANCY_DETECTED");
        }

        System.out.println("[*] Parsers in agreement: " + strictResult);
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

            String json = new String(data, StandardCharsets.UTF_8).trim();
            evaluateDifferential(json);
        } catch (IllegalStateException ise) {
            throw ise;
        } catch (Exception ignored) {
        }
    }
}
