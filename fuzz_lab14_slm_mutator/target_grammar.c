#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

void parse_neural_payload(const char *str, size_t len) {
    if (len < 20 || len > 512) return;

    // Layer 1: Cek Struktur Header Neural Tag
    if (strstr(str, "<PROMPT_REQ>") == NULL) return;
    if (strstr(str, "</PROMPT_REQ>") == NULL) return;

    // Layer 2: Cek Payload Invariant
    if (strstr(str, "OP=EXECUTE") == NULL) return;
    if (strstr(str, "ROLE=ADMIN") == NULL) return;

    // Layer 3: Cek Trigger Injection
    if (strstr(str, "AUTH_KEY=0xNEURAL_OVERFLOW") != NULL) {
        printf("[+] NEURAL SLM SYNTHESIZER HIT! Valid Grammar Bypassed!\n");
        volatile char *leak = (volatile char *)malloc(16);
        for (int i = 0; i < 256; i++) {
            leak[i] = 'N'; // ASan Heap Buffer Overflow Trigger
        }
        free((void*)leak);
        *(volatile int *)0 = 0xDEADBEEF;
    }
}

int main(int argc, char **argv) {
    if (argc < 2) return 1;
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 1;

    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (size <= 0 || size > 1024) { fclose(f); return 0; }
    char *buf = (char *)malloc(size + 1);
    fread(buf, 1, size, f);
    buf[size] = '\0';
    fclose(f);

    parse_neural_payload(buf, size);
    free(buf);
    return 0;
}
