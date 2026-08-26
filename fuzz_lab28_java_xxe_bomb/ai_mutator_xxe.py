import random

XML_TEMPLATES = [
    """<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY %s "%s">
]>
<root>&%s;</root>""",
    """<?xml version="1.0"?>
<!DOCTYPE data [
  <!ENTITY xxe SYSTEM "%s">
]>
<data>&xxe;</data>""",
    """<?xml version="1.0"?>
<message>
  <user>%s</user>
  <content>%s</content>
</message>"""
]

ENTITIES = [
    "XXE_ENTITY_TRIGGER",
    "file:///etc/passwd",
    "http://127.0.0.1:8080/internal",
    "&lol1;&lol1;&lol1;&lol1;"
]

def init(seed):
    random.seed(seed)

def fuzz(buf, add_buf, max_size):
    choice = random.choice([0, 1, 2])
    if choice == 0:
        entity_name = "test"
        entity_val = random.choice(ENTITIES)
        xml = XML_TEMPLATES[0] % (entity_name, entity_val, entity_name)
    elif choice == 1:
        entity_val = random.choice(ENTITIES)
        xml = XML_TEMPLATES[1] % entity_val
    else:
        user = "admin"
        content = "safe_payload"
        xml = XML_TEMPLATES[2] % (user, content)

    return bytearray(xml.encode("utf-8")[:max_size])

def deinit():
    pass
