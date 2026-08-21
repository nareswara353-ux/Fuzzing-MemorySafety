#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>

#define MAX_BRANCHES 16

typedef struct {
    int64_t min_distance[MAX_BRANCHES];
    uint64_t hits[MAX_BRANCHES];
} DistanceTable;

static DistanceTable g_table;

__attribute__((constructor))
void __init_distance_rt(void) {
    for (int i = 0; i < MAX_BRANCHES; i++) {
        g_table.min_distance[i] = 0x7FFFFFFFFFFFFFFFLL;
        g_table.hits[i] = 0;
    }
}

void __record_branch_distance(uint32_t branch_id, int64_t diff) {
    if (branch_id >= MAX_BRANCHES) return;
    g_table.hits[branch_id]++;
    if (diff < g_table.min_distance[branch_id]) {
        g_table.min_distance[branch_id] = diff;
    }
}

__attribute__((destructor))
void __dump_distance_rt(void) {
    FILE *f = fopen("/tmp/branch_distance.bin", "wb");
    if (f) {
        fwrite(&g_table, sizeof(DistanceTable), 1, f);
        fclose(f);
    }
}
