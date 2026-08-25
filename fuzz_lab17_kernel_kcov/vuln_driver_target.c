#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

// Definisi IOCTL Command Structures
#define DRIVER_MAGIC 0x88
#define CMD_REGISTER_CLIENT  0x01
#define CMD_UPDATE_CONFIG    0x02
#define CMD_TRIGGER_DISPATCH 0x03

typedef struct {
    uint32_t client_id;
    uint32_t flags;
    char name[16];
} ClientConfig;

typedef struct {
    uint8_t magic;
    uint8_t cmd;
    uint16_t data_len;
    uint8_t payload[64];
} IoctlPacket;

// Mock KCOV Coverage Tracer
static uint64_t g_kcov_trace[1024];
static uint32_t g_kcov_idx = 0;

void kcov_record_pc(uint64_t pc) {
    if (g_kcov_idx < 1024) {
        g_kcov_trace[g_kcov_idx++] = pc;
    }
}

// Simulasi Kernel IOCTL Dispatcher
int mock_driver_ioctl(const IoctlPacket *pkt, size_t size) {
    kcov_record_pc(0x1000); // PC Trace 1: Entry
    if (size < sizeof(IoctlPacket)) return -1;
    if (pkt->magic != DRIVER_MAGIC) return -2;

    kcov_record_pc(0x1010); // PC Trace 2: Magic Valid

    switch (pkt->cmd) {
        case CMD_REGISTER_CLIENT:
            kcov_record_pc(0x2001);
            printf("[*] Driver: Client Registered.\n");
            break;

        case CMD_UPDATE_CONFIG:
            kcov_record_pc(0x2002);
            if (pkt->data_len > 16) {
                // SINK: Heap Out-of-Bounds Write (Kernel Pool Corruption Simulation)
                printf("[!] KERNEL DRIVER VULN HIT: OOB Slab Overwrite!\n");
                volatile char *kheap = (volatile char *)malloc(16);
                for (int i = 0; i < pkt->data_len && i < 128; i++) {
                    kheap[i] = pkt->payload[i]; // ASan Heap Overflow Trap
                }
                free((void*)kheap);
                *(volatile int *)0 = 0xDEADBEEF;
            }
            break;

        case CMD_TRIGGER_DISPATCH:
            kcov_record_pc(0x2003);
            printf("[*] Driver: Dispatch executed.\n");
            break;

        default:
            kcov_record_pc(0x20FF);
            return -3;
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) return 1;
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 1;

    IoctlPacket pkt;
    memset(&pkt, 0, sizeof(pkt));
    size_t bytes = fread(&pkt, 1, sizeof(pkt), f);
    fclose(f);

    mock_driver_ioctl(&pkt, bytes);
    return 0;
}
