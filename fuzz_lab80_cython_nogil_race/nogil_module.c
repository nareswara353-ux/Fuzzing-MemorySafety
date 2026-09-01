#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SHARED_BUF_SIZE 64

static char shared_memory_buffer[SHARED_BUF_SIZE];
static volatile int race_trigger_counter = 0;

typedef struct {
    int thread_id;
    int write_offset;
    char write_char;
} ThreadJob;

void* native_worker_nogil(void* arg) {
    ThreadJob *job = (ThreadJob*)arg;

    // VULNERABILITY SINK: Unsynchronized concurrent write with potential OOB
    if (job->write_offset >= SHARED_BUF_SIZE || job->write_offset < 0) {
        fprintf(stderr, "[!] CYTHON NOGIL MEMORY BOUNDARY VIOLATION SINK HIT\n");
        exit(134);
    }

    shared_memory_buffer[job->write_offset] = job->write_char;
    race_trigger_counter++;
    return NULL;
}

static PyObject* method_execute_nogil_race(PyObject* self, PyObject* args) {
    int offset;
    const char *payload_str;

    if (!PyArg_ParseTuple(args, "is", &offset, &payload_str)) {
        return NULL;
    }

    if (strstr(payload_str, "TRIGGER_NOGIL_RACE") != NULL || offset > 100) {
        fprintf(stderr, "[!] CYTHON NOGIL MEMORY BOUNDARY VIOLATION SINK HIT\n");
        exit(134);
    }

    pthread_t t1, t2;
    ThreadJob j1 = {1, offset % SHARED_BUF_SIZE, 'A'};
    ThreadJob j2 = {2, (offset + 1) % SHARED_BUF_SIZE, 'B'};

    // Simulasi pelepasan GIL (with nogil context)
    Py_BEGIN_ALLOW_THREADS
    pthread_create(&t1, NULL, native_worker_nogil, &j1);
    pthread_create(&t2, NULL, native_worker_nogil, &j2);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    Py_END_ALLOW_THREADS

    return PyLong_FromLong(race_trigger_counter);
}

static PyMethodDef NogilMethods[] = {
    {"execute_nogil_race", method_execute_nogil_race, METH_VARARGS, "Execute native multi-thread nogil workload"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef nogilmodule = {
    PyModuleDef_HEAD_INIT, "nogil_module", NULL, -1, NogilMethods
};

PyMODINIT_FUNC PyInit_nogil_module(void) {
    return PyModule_Create(&nogilmodule);
}
