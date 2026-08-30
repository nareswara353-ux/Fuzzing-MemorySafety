import random

DELIMITERS = [";", " && ", " || ", " | ", "`", "$("]
COMMANDS = ["id", "whoami", "echo EXPLOIT_CMD_EXEC", "cat /etc/passwd"]
SAFE_ARGS = ["file1.txt", "--verbose", "status", "output.log"]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        delim = random.choice(DELIMITERS)
        cmd = random.choice(COMMANDS)
        if delim == "`":
            payload = f"arg `{cmd}`".encode("utf-8")
        elif delim == "$(":
            payload = f"arg $({cmd})".encode("utf-8")
        else:
            payload = f"arg{delim}{cmd}".encode("utf-8")
    else:
        payload = random.choice(SAFE_ARGS).encode("utf-8")

    return bytearray(payload[:max_size])

def deinit():
    pass
