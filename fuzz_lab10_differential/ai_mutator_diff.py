import random

DIFF_TOKENS = [
    b"007",
    b"010",
    b"00001",
    b"-0",
    b"999999999",
    b"08",
    b"09"
]

def init(seed):
    pass

def fuzz(buf, add_buf, max_size):
    mutated = bytearray(buf)
    
    # 70% injeksi token ambiguitas semantik
    if random.random() < 0.7:
        chosen_token = random.choice(DIFF_TOKENS)
        mutated = bytearray(b"VAL=" + chosen_token)
    else:
        # 30% mutasi numerik acak
        if len(mutated) >= 4:
            mutated[4:] = str(random.randint(0, 9999)).encode()
        else:
            mutated = bytearray(b"VAL=123")

    return mutated[:max_size]

def deinit():
    pass
