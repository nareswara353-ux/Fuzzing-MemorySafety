#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define WASM_MAGIC   0x6d736100 // '\0asm'
#define WASM_VERSION 0x00000001 // Version 1

#define SEC_TYPE   0x01
#define SEC_IMPORT 0x02
#define SEC_FUNC   0x03
#define SEC_MEMORY 0x05
#define SEC_CODE   0x0a

// Opcode WebAssembly Simpel
#define OP_I32_CONST 0x41
#define OP_I32_ADD   0x6a
#define OP_CALL      0x10
#define OP_END       0x0b

void execute_wasm_module(const uint8_t *data, size_t size) {
    if (size < 8) return;

    // Layer 1: Validasi Header WASM Biner
    uint32_t magic = *(uint32_t *)data;
    uint32_t version = *(uint32_t *)(data + 4);

    if (magic != WASM_MAGIC || version != WASM_VERSION) return;

    size_t offset = 8;
    while (offset + 2 <= size) {
        uint8_t sec_id = data[offset++];
        uint8_t sec_len = data[offset++];

        if (offset + sec_len > size) break;

        const uint8_t *sec_body = data + offset;
        offset += sec_len;

        // Evaluasi Code Section (Section 0x0a)
        if (sec_id == SEC_CODE && sec_len >= 4) {
            // Deteksi Bytecode Sequence Pemicu: OP_I32_CONST (0x41) -> OP_I32_ADD (0x6a) -> OP_CALL (0x10)
            if (sec_body[0] == OP_I32_CONST && sec_body[1] == OP_I32_ADD && sec_body[2] == OP_CALL) {
                printf("[!] WASM BYTECODE JIT TRAP HIT: Executing Out-of-Bounds Memory Access!\n");
                volatile char *jit_buf = (volatile char *)malloc(16);
                for (int i = 0; i < sec_len && i < 256; i++) {
                    jit_buf[i] = 'W'; // ASan Heap Buffer Overflow
                }
                free((void *)jit_buf);
                *(volatile int *)0 = 0xDEADBEEF;
            }
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

    if (size <= 0 || size > 1024) { fclose(f); return 0; }
    uint8_t *buf = (uint8_t *)malloc(size);
    fread(buf, 1, size, f);
    fclose(f);

    execute_wasm_module(buf, size);
    free(buf);
    return 0;
}
