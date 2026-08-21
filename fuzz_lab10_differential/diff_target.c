#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>

typedef struct {
    int is_valid;
    int32_t parsed_value;
} ParseResult;

// Parser Alpha: Strict RFC (Tolak leading zero jika panjang angka > 1)
ParseResult parse_alpha(const uint8_t *data, size_t size) {
    ParseResult res = {0, 0};
    if (size < 5 || size > 64) return res;
    if (memcmp(data, "VAL=", 4) != 0) return res;

    const uint8_t *num_str = data + 4;
    size_t num_len = size - 4;

    if (num_len > 1 && num_str[0] == '0') {
        res.is_valid = 0;
        return res;
    }

    int32_t val = 0;
    for (size_t i = 0; i < num_len; i++) {
        if (!isdigit(num_str[i])) return res;
        val = val * 10 + (num_str[i] - '0');
    }

    res.parsed_value = val;
    res.is_valid = 1;
    return res;
}

// Parser Beta: Lenient (Menerima leading zero)
ParseResult parse_beta(const uint8_t *data, size_t size) {
    ParseResult res = {0, 0};
    if (size < 5 || size > 64) return res;
    if (memcmp(data, "VAL=", 4) != 0) return res;

    const uint8_t *num_str = data + 4;
    size_t num_len = size - 4;

    int32_t val = 0;
    for (size_t i = 0; i < num_len; i++) {
        if (!isdigit(num_str[i])) return res;
        val = val * 10 + (num_str[i] - '0');
    }

    res.parsed_value = val;
    res.is_valid = 1;
    return res;
}

int main(int argc, char **argv) {
    if (argc < 2) return 1;
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 1;

    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (size <= 0 || size > 256) { fclose(f); return 0; }
    uint8_t *buf = (uint8_t *)malloc(size);
    fread(buf, 1, size, f);
    fclose(f);

    ParseResult r_alpha = parse_alpha(buf, size);
    ParseResult r_beta = parse_beta(buf, size);

    // DIFFERENTIAL ORACLE: Validasi kesetaraan semantik
    if (r_alpha.is_valid != r_beta.is_valid || (r_alpha.is_valid && r_alpha.parsed_value != r_beta.parsed_value)) {
        fprintf(stderr, "[!] DIFFERENTIAL LOGIC ANOMALY DETECTED!\n");
        free(buf);
        abort(); // Memicu crash signal untuk AFL++
    }

    free(buf);
    return 0;
}
