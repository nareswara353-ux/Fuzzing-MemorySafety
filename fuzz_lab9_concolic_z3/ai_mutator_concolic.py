import struct
import random

try:
    from concolic_solver import solve_symbolic_guards
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from concolic_solver import solve_symbolic_guards

cached_solution = None
mutation_step = 0

def init(seed):
    global cached_solution
    cached_solution = solve_symbolic_guards()

def fuzz(buf, add_buf, max_size):
    global mutation_step
    mutation_step += 1

    mutated = bytearray(buf)
    if len(mutated) < 16:
        mutated.extend(b"\x00" * (16 - len(mutated)))

    if cached_solution:
        magic, x, y, chk = cached_solution
        # Pasang solusi concolic
        mutated[0:4] = struct.pack("<I", magic)
        mutated[4:8] = struct.pack("<I", x)
        mutated[8:12] = struct.pack("<I", y)
        mutated[12:16] = struct.pack("<I", chk)

    # Lakukan stochastic exploration pada payload setelah header
    if mutation_step % 3 == 0 and len(mutated) > 16:
        pos = random.randint(16, len(mutated) - 1)
        mutated[pos] = (mutated[pos] + 1) & 0xFF

    return mutated[:max_size]

def deinit():
    pass
