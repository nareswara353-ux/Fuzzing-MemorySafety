#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#pragma pack(push, 1)
typedef struct {
    char magic[4];       // "PACK"
    uint8_t version;     // 0x02
    uint16_t chunk_count;
    uint16_t payload_len;
} Header;
#pragma pack(pop)

void parse_payload(const uint8_t *data, size_t size) {
    if (size < sizeof(Header)) return;

    const Header *hdr = (const Header *)data;

    // Gate 1: Magic check
    if (memcmp(hdr->magic, "PACK", 4) != 0) return;

    // Gate 2: Version constraint
    if (hdr->version != 0x02) return;

    // Gate 3: State constraint
    if (hdr->chunk_count > 0x10) return;

    const uint8_t *body = data + sizeof(Header);
    size_t body_len = size - sizeof(Header);

    if (body_len < hdr->payload_len) return;

    // Alokasi buffer berdasarkan chunk_count * 16 bytes
    size_t alloc_sz = (size_t)hdr->chunk_count * 16;
    if (alloc_sz == 0) alloc_sz = 16;

    // PATCH: Validasi relasional ukuran buffer vs ukuran copy
    if (hdr->payload_len > alloc_sz) {
        return;
    }

    char *dynamic_buf = (char *)malloc(alloc_sz);
    if (!dynamic_buf) return;

    memcpy(dynamic_buf, body, hdr->payload_len);

    if (dynamic_buf[0] == 0x7F && dynamic_buf[1] == 'E') {
        dynamic_buf[alloc_sz - 1] = '\0';
    }

    free(dynamic_buf);
}

int main(int argc, char **argv) {
    if (argc < 2) return 1;

    FILE *f = fopen(argv[1], "rb");
    if (!f) return 1;

    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (sz <= 0 || sz > 1024 * 64) {
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

    parse_payload(buf, sz);

    free(buf);
    return 0;
}
