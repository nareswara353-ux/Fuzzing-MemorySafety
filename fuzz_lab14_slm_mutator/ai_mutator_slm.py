import random
try:
    from slm_bridge import mutate_with_slm_heuristics, synthesize_structured_seed
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from slm_bridge import mutate_with_slm_heuristics, synthesize_structured_seed

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    if random.random() < 0.6:
        # Gunakan sintesis grammar berbasis model
        res = mutate_with_slm_heuristics(buf)
    else:
        # Mutasi token acak
        res = synthesize_structured_seed()
    return bytearray(res[:max_size])

def deinit():
    pass
