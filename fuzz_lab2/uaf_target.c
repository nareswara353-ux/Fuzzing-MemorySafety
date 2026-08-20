#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct {
    char username[16];
    int privilege_level;
} UserSession;

UserSession *g_session = NULL;

void process_commands(const uint8_t *data, size_t size) {
    size_t offset = 0;

    while (offset < size) {
        uint8_t opcode = data[offset++];

        switch (opcode) {
            case 0x01: // CREATE SESSION
                if (!g_session) {
                    g_session = (UserSession *)malloc(sizeof(UserSession));
                    if (g_session) {
                        strncpy(g_session->username, "guest", 15);
                        g_session->privilege_level = 1;
                    }
                }
                break;

            case 0x02: 
                if (g_session) {
                    free(g_session);
                    g_session = NULL;
                }
                break;

            case 0x03: 
                if (offset + 16 <= size) {
                    char *raw = (char *)malloc(16);
                    if (raw) {
                        memcpy(raw, data + offset, 16);
                    }
                    offset += 16;
                }
                break;

            case 0x04: 
                if (g_session) {
                    // Jika opcode 0x02 dieksekusi sebelumnya, terjadi Use-After-Free
                    if (g_session->privilege_level == 99) {
                        printf("[!] High privilege action executed\n");
                    } else {
                        printf("[*] User: %s, Priv: %d\n", g_session->username, g_session->privilege_level);
                    }
                }
                break;

            default:
                return; // Unknown opcode, terminasi parser
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) return 1;

    FILE *f = fopen(argv[1], "rb");
    if (!f) return 1;

    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (sz <= 0 || sz > 1024) {
        fclose(f);
        return 1;
    }

    uint8_t *buf = (uint8_t *)malloc(sz);
    if (!buf) {
        fclose(f);
        return 1;
    }

    fread(buf, 1, sz, f);
    fclose(f);

    process_commands(buf, sz);

    free(buf);
    return 0;
}
