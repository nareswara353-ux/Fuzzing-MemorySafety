#!/usr/bin/env python3
import ast
import random
import sys

class Mutator(ast.NodeTransformer):
    def __init__(self, chance=0.3):
        self.chance = chance

    def visit_Name(self, node):
        if random.random() < self.chance:
            new_name = random.choice(['x', 'y', 'z', 'foo', 'bar', 'data', 'result'])
            return ast.Name(id=new_name, ctx=node.ctx)
        return node

    def visit_Constant(self, node):
        if random.random() < self.chance:
            if isinstance(node.value, int):
                return ast.Constant(value=node.value + random.randint(-10, 10))
            elif isinstance(node.value, str):
                return ast.Constant(value=node.value + random.choice(['', ' ', '!', '?']))
        return node

    def visit_BinOp(self, node):
        if random.random() < self.chance:
            ops = [ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod]
            node.op = random.choice(ops)()
        self.generic_visit(node)
        return node

def mutate_code(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code
    mutator = Mutator()
    try:
        new_tree = mutator.visit(tree)
        ast.fix_missing_locations(new_tree)
        return ast.unparse(new_tree)
    except Exception:
        return code

def mutate_string_based(code):
    lines = code.splitlines()
    if not lines:
        return code
    if random.random() < 0.1 and len(lines) > 1:
        del lines[random.randrange(len(lines))]
    if random.random() < 0.1:
        lines.insert(random.randrange(len(lines)+1),
                     random.choice(['print("hello")', 'x=1', 'pass']))
    if random.random() < 0.1 and len(code) > 10:
        idx = random.randrange(len(code))
        code = code[:idx] + random.choice('abcdefghijklmnopqrstuvwxyz') + code[idx+1:]
    return '\n'.join(lines)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: ai_mutator_lab90.py <input_file>")
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        code = f.read()
    mutated = mutate_code(code)
    if mutated == code:
        mutated = mutate_string_based(code)
    print(mutated)
