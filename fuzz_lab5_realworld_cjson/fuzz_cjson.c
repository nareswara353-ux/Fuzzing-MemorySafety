#include <stdio.h>
#include <stdlib.h>
#include "cJSON.h"

int main(int argc, char **argv) {
    if (argc < 2) return 1;

    FILE *f = fopen(argv[1], "rb");
    if (!f) return 1;

    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (len <= 0 || len > 1024 * 1024) {
        fclose(f);
        return 0;
    }

    char *data = (char *)malloc(len + 1);
    if (!data) {
        fclose(f);
        return 0;
    }

    fread(data, 1, len, f);
    data[len] = '\0';
    fclose(f);

    // Parse JSON
    cJSON *json = cJSON_Parse(data);
    if (json) {
        // Eksplorasi branch print & minification
        char *rendered = cJSON_PrintUnformatted(json);
        if (rendered) {
            free(rendered);
        }
        cJSON_Delete(json);
    }

    free(data);
    return 0;
}
