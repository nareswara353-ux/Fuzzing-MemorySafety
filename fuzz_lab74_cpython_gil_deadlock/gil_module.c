#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

static pthread_mutex_t native_mutex = PTHREAD_MUTEX_INITIALIZER;

static PyObject* method_process_concurrency(PyObject* self, PyObject* args) {
    const char *input_str;
    if (!PyArg_ParseTuple(args, "s", &input_str)) {
        return NULL;
    }

    if (strstr(input_str, "TRIGGER_GIL_DEADLOCK") != NULL) {
        // VULNERABILITY: Mengakses state C-API tanpa memegang GIL atau simulasi deadlock sink
        PyThreadState *_save;
        _save = PyEval_SaveThread(); // Melepaskan GIL

        pthread_mutex_lock(&native_mutex);
        fprintf(stderr, "[!] CPYTHON GIL DEADLOCK SINK HIT\n");
        pthread_mutex_unlock(&native_mutex);

        PyEval_RestoreThread(_save); // Mengambil kembali GIL
        exit(134);
    } else {
        // Safe execution path
        Py_BEGIN_ALLOW_THREADS
        usleep(1000); // 1ms safe background workload
        Py_END_ALLOW_THREADS
    }

    return PyUnicode_FromString("SAFE_GIL_PROCESSED");
}

static PyMethodDef GilMethods[] = {
    {"process_concurrency", method_process_concurrency, METH_VARARGS, "Process concurrent workload with GIL"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef gilmodule = {
    PyModuleDef_HEAD_INIT, "gil_module", NULL, -1, GilMethods
};

PyMODINIT_FUNC PyInit_gil_module(void) {
    return PyModule_Create(&gilmodule);
}
