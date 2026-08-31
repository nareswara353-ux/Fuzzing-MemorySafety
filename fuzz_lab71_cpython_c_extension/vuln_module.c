#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <string.h>

static PyObject* method_process_data(PyObject* self, PyObject* args) {
    char *input_str;
    char buffer[64]; // Fixed size buffer

    if (!PyArg_ParseTuple(args, "s", &input_str)) {
        return NULL;
    }

    // VULNERABILITY: Unsafe copy to fixed-size buffer
    if (strlen(input_str) > 200) { // Trigger for fuzzer
        fprintf(stderr, "[!] CPYTHON C-EXTENSION BUFFER OVERFLOW HIT\n");
        strcpy(buffer, input_str); // Classic overflow
    } else {
        strncpy(buffer, input_str, sizeof(buffer)-1);
        buffer[sizeof(buffer)-1] = '\0';
    }

    return PyUnicode_FromString("OK");
}

static PyMethodDef VulnMethods[] = {
    {"process_data", method_process_data, METH_VARARGS, "Process string in C"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef vulnmodule = {
    PyModuleDef_HEAD_INIT, "vuln_module", NULL, -1, VulnMethods
};

PyMODINIT_FUNC PyInit_vuln_module(void) {
    return PyModule_Create(&vulnmodule);
}
