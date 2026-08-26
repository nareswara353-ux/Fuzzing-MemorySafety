import struct
import random

STREAM_MAGIC = 0xACED
STREAM_VERSION = 0x0005
TC_OBJECT = 0x73
TC_CLASSDESC = 0x72

GADGET_CANDIDATES = [
    b"org.vulnerable.GadgetPayload",
    b"com.app.model.EXPLOIT_GADGET_TRIGGER_BEAN",
    b"java.util.Collections$UnmodifiableSet",
    b"org.safe.UserSession"
]

def init(seed):
    random.seed(seed)

def synthesize_serialized_object(class_name_bytes):
    # Header: Magic(2B), Version(2B), TC_OBJECT(1B), TC_CLASSDESC(1B), NameLen(2B), NameBytes
    header = struct.pack(">HHBBH", STREAM_MAGIC, STREAM_VERSION, TC_OBJECT, TC_CLASSDESC, len(class_name_bytes))
    return header + class_name_bytes

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        # Injeksi gadget chain pemicu sink
        class_name = random.choice(GADGET_CANDIDATES)
    else:
        # Mutasi nama kelas acak
        random_str = "".join(random.choice("abcdefghijklmnopqrstuvwxyz.") for _ in range(random.randint(6, 20))).encode()
        class_name = random_str

    raw = synthesize_serialized_object(class_name)
    return bytearray(raw[:max_size])

def deinit():
    pass
