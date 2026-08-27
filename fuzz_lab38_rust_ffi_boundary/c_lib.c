#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

void process_c_payload(const uint8_t *data, size_t len) {
    if (len < 8) return;
    uint32_t magic = *(uint32_t *)data;
    if (magic != 0x46464924) return;
    
    uint8_t cmd = data[4];
    if (cmd == 0xCC) {
        fprintf(stderr, "[!] RUST-C FFI BOUNDARY CORRUPTION HIT\n");
        abort();
    }
}
