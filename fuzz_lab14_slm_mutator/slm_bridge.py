#!/usr/bin/env python3
import random

GRAMMAR_TEMPLATES = [
    "<PROMPT_REQ> OP={op}; ROLE={role}; AUTH_KEY={auth} </PROMPT_REQ>",
    "<PROMPT_REQ>\n  <ACTION>{op}</ACTION>\n  <USER>{role}</USER>\n  <KEY>{auth}</KEY>\n</PROMPT_REQ>"
]

OPERATIONS = ["EXECUTE", "READ", "QUERY", "STATUS"]
ROLES = ["ADMIN", "GUEST", "SYSTEM", "ROOT"]
KEYS = ["0xNEURAL_OVERFLOW", "0x1337", "0xVALID_TOKEN", "0xANON"]

def synthesize_structured_seed():
    template = random.choice(GRAMMAR_TEMPLATES)
    payload = template.format(
        op=random.choice(OPERATIONS),
        role=random.choice(ROLES),
        auth=random.choice(KEYS)
    )
    return payload.encode("utf-8")

def mutate_with_slm_heuristics(data):
    try:
        text = data.decode("utf-8", errors="ignore")
    except Exception:
        return synthesize_structured_seed()

    # Injeksi grammar valid terstruktur
    if "<PROMPT_REQ>" not in text:
        return synthesize_structured_seed()

    # Pertahankan format semantik namun suntikkan token target
    mutated = "<PROMPT_REQ> OP=EXECUTE; ROLE=ADMIN; AUTH_KEY=0xNEURAL_OVERFLOW </PROMPT_REQ>"
    return mutated.encode("utf-8")

if __name__ == "__main__":
    print(synthesize_structured_seed().decode())
