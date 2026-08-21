#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

// Deklarasi runtime probe eksternal
extern void __record_branch_distance(uint32_t branch_id, int64_t diff);

void process_data(const uint8_t *data, size_t size) {
    if (size < 16) return;

    uint32_t magic = *(uint32_t*)(data);
    int32_t val1 = *(int32_t*)(data + 4);
    int32_t val2 = *(int32_t*)(data + 8);
    int32_t checksum = *(int32_t*)(data + 12);

    // Stage 1: Header Check
    int64_t d1 = (int64_t)magic - (int64_t)0x584c4c56; // "VLLX"
    __record_branch_distance(1, d1 >= 0 ? d1 : -d1);
    if (magic != 0x584c4c56) return;

    // Stage 2: Arithmetic Constraint (val1 + val2 == 0x1337)
    int64_t d2 = (int64_t)(val1 + val2) - (int64_t)0x1337;
    __record_branch_distance(2, d2 >= 0 ? d2 : -d2);
    if ((val1 + val2) != 0x1337) return;

    // Stage 3: Dynamic Multiplier (val1 * 3 == checksum)
    int64_t d3 = (int64_t)(val1 * 3) - (int64_t)checksum;
    __record_branch_distance(3, d3 >= 0 ? d3 : -d3);
    if ((val1 * 3) != checksum) return;

    // Stage 4: Trigger ASan Heap Buffer Overflow
    printf("[!] All Arithmetic Guards Passed! Triggering Target ASan Crash...\n");
    char *buf = (char *)malloc(16);
    memset(buf, 'B', 64); // ASan Heap Buffer Overflow
    free(buf);
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

    process_data(buf, size);
    free(buf);
    return 0;
}
