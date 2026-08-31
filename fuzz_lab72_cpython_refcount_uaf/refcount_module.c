#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <string.h>

static PyObject* method_trigger_uaf(PyObject* self, PyObject* args) {
    const char *input_str;
    if (!PyArg_ParseTuple(args, "s", &input_str)) {
        return NULL;
    }

    PyObject *temp_obj = PyUnicode_FromString("TRANSIENT_CPYTHON_OBJECT");
    if (!temp_obj) {
        Py_RETURN_NONE;
    }

    if (strstr(input_str, "TRIGGER_UAF_DECREF") != NULL) {
        // VULNERABILITY: Premature decref menurunkan refcount ke 0 (deallokasi)
        Py_DECREF(temp_obj);

        fprintf(stderr, "[!] CPYTHON REFCOUNT USE-AFTER-FREE HIT\n");
        // Akses dangling pointer pasca deallokasi (UAF / Double Free)
        Py_DECREF(temp_obj);
    } else {
        Py_DECREF(temp_obj); // Pelepasan memori normal di akhir alur
    }

    return PyUnicode_FromString("SAFE_REFCOUNT_PROCESSED");
}

static PyMethodDef RefcountMethods[] = {
    {"trigger_uaf", method_trigger_uaf, METH_VARARGS, "Trigger premature decref and UAF"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef refcountmodule = {
    PyModuleDef_HEAD_INIT, "refcount_module", NULL, -1, RefcountMethods
};

PyMODINIT_FUNC PyInit_refcount_module(void) {
    return PyModule_Create(&refcountmodule);
}
