#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

typedef enum {
    STATE_INIT = 0,
    STATE_HANDSHAKE_DONE,
    STATE_AUTHENTICATED,
    STATE_TERMINATED
} SessionState;

#define MSG_HELLO 0x01
#define MSG_AUTH  0x02
#define MSG_DATA  0x03
#define MSG_QUIT  0x04

#pragma pack(push, 1)
typedef struct {
    uint8_t type;
    uint8_t length;
} MessageHeader;
#pragma pack(pop)

void process_stateful_session(const uint8_t *stream, size_t total_size) {
    SessionState state = STATE_INIT;
    size_t offset = 0;

    while (offset + sizeof(MessageHeader) <= total_size && state != STATE_TERMINATED) {
        const MessageHeader *hdr = (const MessageHeader *)(stream + offset);
        offset += sizeof(MessageHeader);

        if (offset + hdr->length > total_size) break;
        const uint8_t *body = stream + offset;
        offset += hdr->length;

        switch (hdr->type) {
            case MSG_HELLO:
                if (state == STATE_INIT && hdr->length >= 4 && memcmp(body, "HELO", 4) == 0) {
                    state = STATE_HANDSHAKE_DONE;
                }
                break;

            case MSG_AUTH:
                if (state == STATE_HANDSHAKE_DONE && hdr->length >= 4) {
                    uint32_t auth_token = *(uint32_t *)body;
                    if (auth_token == 0x1337C0DE) {
                        state = STATE_AUTHENTICATED;
                    }
                }
                break;

            case MSG_DATA:
                if (state == STATE_AUTHENTICATED) {
                    if (hdr->length > 16) {
                        // SINK: Heap Buffer Overflow pada state terotentikasi
                        printf("[!] STATEFUL PROTOCOL CRASH HIT: Buffer overflow in AUTHENTICATED state!\n");
                        volatile char *buf = (volatile char *)malloc(16);
                        for (int i = 0; i < hdr->length && i < 128; i++) {
                            buf[i] = body[i]; // ASan Heap Overflow Trap
                        }
                        free((void *)buf);
                        *(volatile int *)0 = 0xDEADBEEF;
                    }
                }
                break;

            case MSG_QUIT:
                state = STATE_TERMINATED;
                break;

            default:
                break;
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

    process_stateful_session(buf, size);
    free(buf);
    return 0;
}
