#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static PyObject* method_allocate_and_mutate(PyObject* self, PyObject* args) {
    int alloc_size;
    int write_len;
    const char *payload_data;

    if (!PyArg_ParseTuple(args, "iis", &alloc_size, &write_len, &payload_data)) {
        return NULL;
    }

    if (alloc_size <= 0 || alloc_size > 512) {
        alloc_size = 64; // Default small-object size-class
    }

    // Menggunakan allocator internal pymalloc CPython
    char *block = (char*)PyObject_Malloc(alloc_size);
    if (!block) {
        return PyErr_NoMemory();
    }

    // VULNERABILITY SINK: Penulisan melebihi size-class block (Pool boundary overflow)
    if (write_len > alloc_size || strstr(payload_data, "TRIGGER_PYMALLOC_CORRUPTION") != NULL) {
        fprintf(stderr, "[!] CPYTHON PYMALLOC ARENA BOUNDARY SINK HIT\n");
        PyObject_Free(block);
        exit(134);
    }

    memcpy(block, payload_data, (size_t)(write_len < alloc_size ? write_len : alloc_size));
    PyObject_Free(block);

    return PyUnicode_FromString("SAFE_PYMALLOC_OPERATION");
}

static PyMethodDef PymallocMethods[] = {
    {"allocate_and_mutate", method_allocate_and_mutate, METH_VARARGS, "Test pymalloc pool allocations"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef pymallocmodule = {
    PyModuleDef_HEAD_INIT, "pymalloc_module", NULL, -1, PymallocMethods
};

PyMODINIT_FUNC PyInit_pymalloc_module(void) {
    return PyModule_Create(&pymallocmodule);
}
