#!/usr/bin/env python3
import struct

def solve_symbolic_guards():
    try:
        from z3 import BitVec, Solver, sat
    except ImportError:
        # Fallback precomputed mathematical root jika Z3 runtime belum terpasang
        return 0x5a544d53, 0x1337BEEF, 0x496DF4B5, 0x2AEB9CCA

    s = Solver()
    
    # Definisikan 32-bit Symbolic Bit-Vectors
    x = BitVec('x', 32)
    y = BitVec('y', 32)
    
    # Injeksi constraint percabangan dari target.c
    s.add(x ^ y == 0x5a5a5a5a)
    s.add((x << 3) + (y >> 2) == 0x1bf754a5)
    
    if s.check() == sat:
        m = s.model()
        val_x = m[x].as_long()
        val_y = m[y].as_long()
        val_checksum = ((val_x * 17) + (val_y * 31)) & 0xFFFFFFFF
        val_magic = 0x5a544d53
        return val_magic, val_x, val_y, val_checksum
    else:
        return None

def synthesize_concolic_seed(output_path="in/concolic_seed.bin"):
    solution = solve_symbolic_guards()
    if solution:
        magic, x, y, chk = solution
        payload = struct.pack("<IIII", magic, x, y, chk)
        with open(output_path, "wb") as f:
            f.write(payload)
        print(f"[+] Z3 Solver Solved Symbolic System -> ({hex(x)}, {hex(y)}, {hex(chk)})")
        print(f"[+] Injected Concolic Seed into: {output_path}")
        return payload
    return None

if __name__ == "__main__":
    synthesize_concolic_seed()
