#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int id;
    int length;
    char data[32];
} DataPayload;

int process_native_payload(DataPayload *payload) {
    if (!payload) {
        return -1;
    }

    if (payload->length > 32 || strstr(payload->data, "TRIGGER_CTYPES_CORRUPTION") != NULL) {
        fprintf(stderr, "[!] PYTHON CTYPES NATIVE MEMORY CORRUPTION SINK HIT\n");
        exit(134);
    }

    return 0;
}
