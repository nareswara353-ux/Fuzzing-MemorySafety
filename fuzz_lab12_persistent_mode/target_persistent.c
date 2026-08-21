#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

// Deklarasi antarmuka in-memory zero-copy AFL++
#ifdef __AFL_HAVE_MANUAL_CONTROL
__AFL_FUZZ_INIT();
#endif

void parse_in_memory_packet(const uint8_t *buf, size_t len) {
    if (len < 8) return;

    // Header Protocol: 'FAST'
    if (buf[0] != 'F' || buf[1] != 'A' || buf[2] != 'S' || buf[3] != 'T') return;

    uint32_t payload_len = *(uint32_t*)(buf + 4);
    if (payload_len > 1024) return;

    if (len >= 8 + payload_len && payload_len >= 4) {
        // Trigger condition: Target sink
        if (buf[8] == 'B' && buf[9] == 'O' && buf[10] == 'O' && buf[11] == 'M') {
            printf("[!] PERSISTENT MODE TRIGGER HIT! Executing Memory Corruption...\n");
            volatile char *leak = (volatile char *)malloc(16);
            for (int i = 0; i < 256; i++) {
                leak[i] = 'P'; // ASan Heap Buffer Overflow
            }
            free((void*)leak);
            *(volatile int *)0 = 0xDEADBEEF;
        }
    }
}

int main(int argc, char **argv) {
    #ifdef __AFL_HAVE_MANUAL_CONTROL
    __AFL_INIT();
    #endif

    unsigned char *buf = __AFL_FUZZ_TESTCASE_BUF;

    // In-Memory Persistent Loop: 100.000 iterasi per 1 proses fork
    while (__AFL_LOOP(100000)) {
        int len = __AFL_FUZZ_TESTCASE_LEN;
        if (len > 0) {
            parse_in_memory_packet(buf, len);
        }
    }

    return 0;
}
