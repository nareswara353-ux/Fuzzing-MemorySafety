#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef void* napi_env;
typedef void* napi_value;
typedef void* napi_callback_info;
typedef napi_value (*napi_callback)(napi_env env, napi_callback_info info);

int napi_get_cb_info(napi_env env, napi_callback_info cbinfo, size_t* argc, napi_value* argv, napi_value* this_arg, void** data);
int napi_get_value_string_utf8(napi_env env, napi_value value, char* buf, size_t bufsize, size_t* result);
int napi_create_function(napi_env env, const char* utf8name, size_t length, napi_callback cb, void* data, napi_value* result);
int napi_set_named_property(napi_env env, napi_value object, const char* utf8name, napi_value value);

napi_value ProcessNativeBuffer(napi_env env, napi_callback_info info) {
    size_t argc = 1;
    napi_value argv[1];
    napi_get_cb_info(env, info, &argc, argv, NULL, NULL);

    char buf[128];
    size_t copied = 0;
    napi_get_value_string_utf8(env, argv[0], buf, sizeof(buf), &copied);

    if (strstr(buf, "CRASH_NAPI_OVERFLOW") != NULL) {
        fprintf(stderr, "[!] N-API NATIVE ADDON BUFFER OVERFLOW HIT\n");
        abort();
    }

    return NULL;
}

napi_value napi_register_module_v1(napi_env env, napi_value exports) {
    napi_value fn;
    napi_create_function(env, "processNativeBuffer", -1, ProcessNativeBuffer, NULL, &fn);
    napi_set_named_property(env, exports, "processNativeBuffer", fn);
    return exports;
}
