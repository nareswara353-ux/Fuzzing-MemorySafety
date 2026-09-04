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
    if (!result) {
        PyErr_Clear();   // ignore error
    } else {
        Py_DECREF(result);
    }
    Py_EndInterpreter(sub_tstate);
    PyThreadState_Swap(main_tstate);
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
    if (!result) {
        PyErr_SetString(PyExc_RuntimeError, "Execution failed in subinterpreter");
        Py_EndInterpreter(sub_tstate);
        PyThreadState_Swap(main_tstate);
        return NULL;
    }
    // BUG: return object from destroyed subinterpreter
    Py_EndInterpreter(sub_tstate);
    PyThreadState_Swap(main_tstate);
    return result;
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
