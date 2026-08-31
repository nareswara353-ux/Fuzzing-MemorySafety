import sys
import os
import ctypes

class DataPayload(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("length", ctypes.c_int),
        ("data", ctypes.c_char * 32)
    ]

def load_native_lib():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(current_dir, "libnative_mem.so")
    if not os.path.exists(lib_path):
        return None
    return ctypes.CDLL(lib_path)

def process_file_input(file_path):
    if not os.path.exists(file_path):
        return

    lib = load_native_lib()
    if not lib:
        sys.stderr.write("Native shared library not found\n")
        return

    with open(file_path, "rb") as f:
        raw_bytes = f.read()

    if len(raw_bytes) < ctypes.sizeof(DataPayload):
        return

    payload_struct = DataPayload.from_buffer_copy(raw_bytes[:ctypes.sizeof(DataPayload)])
    
    lib.process_native_payload.argtypes = [ctypes.POINTER(DataPayload)]
    lib.process_native_payload.restype = ctypes.c_int

    ret = lib.process_native_payload(ctypes.byref(payload_struct))
    print(f"[*] Native ctypes invocation completed safely with code: {ret}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_file_input(sys.argv[1])
