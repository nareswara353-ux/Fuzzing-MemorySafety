#include <Python.h>
#include <stdio.h>

static PyObject* run_code_safe(PyObject* self, PyObject* args) {
    const char* code;
    if (!PyArg_ParseTuple(args, "s", &code)) {
        return NULL;
    }
    PyThreadState* main_tstate = PyThreadState_Get();
    PyThreadState* sub_tstate = Py_NewInterpreter();
    if (!sub_tstate) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create subinterpreter");
        return NULL;
    }
    PyThreadState_Swap(sub_tstate);
    PyObject* result = PyRun_String(code, Py_file_input,
                                    PyEval_GetGlobals(), PyEval_GetLocals());
    PyThreadState_Swap(main_tstate);
    Py_EndInterpreter(sub_tstate);
    if (!result) {
        return NULL;
    }
    Py_DECREF(result);
    Py_RETURN_NONE;
}

static PyObject* run_code_buggy(PyObject* self, PyObject* args) {
    const char* code;
    if (!PyArg_ParseTuple(args, "s", &code)) {
        return NULL;
    }
    PyThreadState* main_tstate = PyThreadState_Get();
    PyThreadState* sub_tstate = Py_NewInterpreter();
    if (!sub_tstate) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create subinterpreter");
        return NULL;
    }
    PyThreadState_Swap(sub_tstate);
    PyObject* result = PyRun_String(code, Py_file_input,
                                    PyEval_GetGlobals(), PyEval_GetLocals());
    PyThreadState_Swap(main_tstate);
    // BUG: subinterpreter dihancurkan, tetapi result (yang berasal dari subinterpreter)
    // tetap dikembalikan. Ini menyebabkan dangling object.
    Py_EndInterpreter(sub_tstate);
    if (!result) {
        return NULL;
    }
    return result;  // berbahaya: objek milik interpreter yang sudah mati
}

static PyMethodDef SubinterpreterMethods[] = {
    {"run_code_safe", run_code_safe, METH_VARARGS, "Run code safely in a new subinterpreter."},
    {"run_code_buggy", run_code_buggy, METH_VARARGS, "Buggy: returns object from destroyed subinterpreter."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef subinterpretermodule = {
    PyModuleDef_HEAD_INIT,
    "subinterpreter_target",
    NULL,
    -1,
    SubinterpreterMethods
};

PyMODINIT_FUNC PyInit_subinterpreter_target(void) {
    return PyModule_Create(&subinterpretermodule);
}
