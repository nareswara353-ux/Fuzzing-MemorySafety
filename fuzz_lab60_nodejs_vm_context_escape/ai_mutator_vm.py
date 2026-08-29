import random

ESCAPE_PAYLOADS = [
    b"this.constructor.constructor('return { isHostProcess: true }')()",
    b"(() => { throw new Error('ESCAPE_TRIGGERED'); })()",
    b"const hostProc = this.constructor.constructor('return \"CRITICAL_VM_ESCAPE\"')(); hostProc;"
]

SAFE_PAYLOADS = [
    b"data.value * 2;",
    b"const a = 10; const b = 20; a + b;",
    b"'result: ' + data.value;"
]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        payload = random.choice(ESCAPE_PAYLOADS)
    else:
        payload = random.choice(SAFE_PAYLOADS)

    return bytearray(payload[:max_size])

def deinit():
    pass
