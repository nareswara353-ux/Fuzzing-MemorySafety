#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define MAX_TAINT_BYTES 128

typedef struct {
    uint8_t tainted_mask[MAX_TAINT_BYTES];
    uint32_t active_count;
} TaintMap;

static TaintMap g_taint_map;

__attribute__((constructor))
void __init_taint_rt(void) {
    memset(&g_taint_map, 0, sizeof(TaintMap));
}

// Catat bahwa byte pada rentang [start_offset, start_offset + len) mempengaruhi percabangan
void __mark_tainted_range(uint32_t start_offset, uint32_t len) {
    for (uint32_t i = 0; i < len && (start_offset + i) < MAX_TAINT_BYTES; i++) {
        if (g_taint_map.tainted_mask[start_offset + i] == 0) {
            g_taint_map.tainted_mask[start_offset + i] = 1;
            g_taint_map.active_count++;
        }
    }
}

__attribute__((destructor))
void __dump_taint_map(void) {
    FILE *f = fopen("/tmp/tainted_offsets.tmp", "wb");
    if (f) {
        fwrite(&g_taint_map, sizeof(TaintMap), 1, f);
        fclose(f);
        rename("/tmp/tainted_offsets.tmp", "/tmp/tainted_offsets.bin");
    }
}
