#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define CLUSTER_MAGIC 0x54534944 // 'DIST' Little-Endian

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint16_t node_id;
    uint16_t seq_id;
    uint8_t cmd;
    uint8_t payload_len;
    uint8_t data[64];
} ClusterPacket;
#pragma pack(pop)

void process_cluster_packet(const ClusterPacket *pkt, size_t size) {
    if (size < sizeof(ClusterPacket) - 64) return;

    // Layer 1: Validasi Header Cluster Magic
    if (pkt->magic != CLUSTER_MAGIC) return;

    // Layer 2: Routing Command Dispatcher
    if (pkt->cmd == 0xCC) { // Cross-Node Broadcast Sync Command
        if (pkt->payload_len >= 16) {
            if (memcmp(pkt->data, "CLUSTER_SYNC_ALL", 16) == 0) {
                // SINK: Distributed Race / Buffer Corruption Trap
                printf("[!] DISTRIBUTED CLUSTER CRASH HIT: Cross-Node Payload Triggered Heap Overflow!\n");
                volatile char *buf = (volatile char *)malloc(16);
                for (int i = 0; i < 256; i++) {
                    buf[i] = 'C'; // ASan Heap Buffer Overflow
                }
                free((void *)buf);
                *(volatile int *)0 = 0xDEADBEEF;
            }
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) return 1;
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 1;

    ClusterPacket pkt;
    memset(&pkt, 0, sizeof(pkt));
    size_t read_bytes = fread(&pkt, 1, sizeof(pkt), f);
    fclose(f);

    process_cluster_packet(&pkt, read_bytes);
    return 0;
}
