#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

extern void __mark_tainted_range(uint32_t start_offset, uint32_t len);

void parse_packet(const uint8_t *data, size_t size) {
    if (size < 24) return;

    // Stage 1: Validasi Header (Offset 0..3)
    __mark_tainted_range(0, 4);
    if (memcmp(data, "DTA!", 4) != 0) return;

    // Stage 2: Validasi Command Type (Offset 8..9)
    __mark_tainted_range(8, 2);
    uint16_t cmd = *(uint16_t*)(data + 8);
    if (cmd != 0x4141) return; // 'AA'

    // Stage 3: Validasi Target Key (Offset 16..19)
    __mark_tainted_range(16, 4);
    uint32_t key = *(uint32_t*)(data + 16);
    if (key != 0x1337C0DE) return;

    // VULNERABILITY SINK: ASan Heap Buffer Overflow
    printf("[+] DTA TAINT HIT! All critical tainted offsets matched!\n");
    volatile char *buf = (volatile char *)malloc(16);
    for (int i = 0; i < 256; i++) {
        buf[i] = 'T';
    }
    free((void*)buf);
    *(volatile int *)0 = 0xDEADBEEF;
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

    parse_packet(buf, size);
    free(buf);
    return 0;
}
