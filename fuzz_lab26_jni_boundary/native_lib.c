#include <jni.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

JNIEXPORT void JNICALL Java_NativeBridge_processNative(JNIEnv *env, jobject obj, jbyteArray data, jint len) {
    if (len < 8) return;

    jbyte *bytes = (*env)->GetByteArrayElements(env, data, NULL);
    if (!bytes) return;

    uint32_t magic = *(uint32_t *)bytes;
    if (magic == 0x494e4a24) {
        uint32_t sub_cmd = *(uint32_t *)(bytes + 4);
        if (sub_cmd == 0xdeadc0de) {
            char *leak = (char *)malloc(16);
            for (int i = 0; i < 256; i++) {
                leak[i] = 'J';
            }
            free(leak);
            *(volatile int *)0 = 0x1337;
        }
    }

    (*env)->ReleaseByteArrayElements(env, data, bytes, JNI_ABORT);
}
