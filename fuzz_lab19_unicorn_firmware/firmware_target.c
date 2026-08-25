#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define MMIO_UART_STATUS 0x40000000
#define MMIO_UART_DATA   0x40000004

// Mock MMIO Peripheral Hardware Register
volatile uint32_t *mock_mmio_status = NULL;

#pragma pack(push, 1)
typedef struct {
    char magic[4];        // 'FIRM'
    uint32_t device_id;   // 0x00010002
    uint8_t cmd;          // Command Type
    uint16_t data_len;    // Payload length
    uint8_t payload[64];  // Data
} FirmwarePacket;
#pragma pack(pop)

void process_firmware_packet(const FirmwarePacket *pkt, size_t size) {
    if (size < sizeof(FirmwarePacket) - 64) return;

    // Layer 1: Validasi Flash Magic
    if (memcmp(pkt->magic, "FIRM", 4) != 0) return;

    // Layer 2: Validasi Device Identity (ARM Device UUID)
    if (pkt->device_id != 0x00010002) return;

    // Layer 3: Peripheral MMIO Status Check (Hardware Ready Simulation)
    uint32_t status_val = 0x01; // Mock UART TX/RX Ready
    if (status_val != 0x01) return;

    // Layer 4: Command Handler Evaluation
    if (pkt->cmd == 0xEE) { // OTA Firmware Update / Diagnostic Command
        if (pkt->data_len > 16) {
            // SINK: Embedded Buffer Overflow (SRAM Memory Corruption)
            printf("[!] FIRMWARE CORRUPTION HIT: Overwriting Peripheral Memory Map!\n");
            volatile char *sram_buf = (volatile char *)malloc(16);
            for (int i = 0; i < pkt->data_len && i < 128; i++) {
                sram_buf[i] = pkt->payload[i]; // ASan / Fault Trigger
            }
            free((void*)sram_buf);
            *(volatile int *)0 = 0xDEADBEEF;
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) return 1;
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 1;

    FirmwarePacket pkt;
    memset(&pkt, 0, sizeof(pkt));
    size_t read_bytes = fread(&pkt, 1, sizeof(pkt), f);
    fclose(f);

    process_firmware_packet(&pkt, read_bytes);
    return 0;
}
