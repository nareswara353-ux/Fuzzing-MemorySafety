#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

// Format Protokol Proprietary Tertutup (Black-Box Target)
// [0..3]: Magic 'BIN$'
// [4..7]: CRC Key 0x4B4C4142 ('BALK' Little-Endian)
// [8..11]: Data Length
// [12..]: Payload buffer

void execute_proprietary_routine(const uint8_t *data, size_t size) {
    if (size < 16) return;

    if (memcmp(data, "BIN$", 4) != 0) return;

    uint32_t secret_key = *(uint32_t*)(data + 4);
    if (secret_key != 0x4B4C4142) return;

    uint32_t payload_len = *(uint32_t*)(data + 8);
    if (payload_len > 128) return;

    // Vulnerability Sink: Stack Buffer Overflow
    if (size >= 12 + payload_len && payload_len >= 32) {
        if (data[12] == 'C' && data[13] == 'O' && data[14] == 'R' && data[15] == 'E') {
            printf("[!] BLACK-BOX BINARY EXPLOIT HIT! Triggering Memory Crash...\n");
            volatile char *leak = (volatile char *)malloc(16);
            for (int i = 0; i < 256; i++) {
                leak[i] = 'X';
            }
            free((void*)leak);
            *(volatile int *)0 = 0xDEADBEEF; // Crash Trap
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) return 1;
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 1;

    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (size <= 0 || size > 512) { fclose(f); return 0; }
    uint8_t *buf = (uint8_t *)malloc(size);
    fread(buf, 1, size, f);
    fclose(f);

    execute_proprietary_routine(buf, size);
    free(buf);
    return 0;
}
