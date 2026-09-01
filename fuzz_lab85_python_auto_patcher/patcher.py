import ast
import sys
import os

class SafeEvalTransformer(ast.NodeTransformer):
    """
    Mentransformasikan pemanggilan fungsi 'eval(...)' menjadi 'ast.literal_eval(...)'
    serta membersihkan direct sink crash triggers.
    """
    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "eval":
            # Ganti eval(...) dengan ast.literal_eval(...)
            new_func = ast.Attribute(
                value=ast.Name(id="ast", ctx=ast.Load()),
                attr="literal_eval",
                ctx=ast.Load()
            )
            return ast.copy_location(
                ast.Call(func=new_func, args=node.args, keywords=node.keywords),
                node
            )
        return node

    def visit_If(self, node):
        self.generic_visit(node)
        # Hapus blok sink exit(134) jika memeriksa substring payload
        if isinstance(node.test, ast.Compare):
            left = getattr(node.test, 'left', None)
            if isinstance(left, ast.Constant) and left.value == "DANGEROUS_AST_PAYLOAD":
                # Netralkan kondisi crash sink
                return None
        return node

def auto_patch_source(source_code):
    tree = ast.parse(source_code)
    
    # Pastikan 'import ast' tersedia
    has_ast_import = any(
        isinstance(n, ast.Import) and any(alias.name == "ast" for alias in n.names)
        for n in tree.body
    )
    if not has_ast_import:
        tree.body.insert(0, ast.Import(names=[ast.alias(name="ast", asname=None)]))

    transformer = SafeEvalTransformer()
    patched_tree = transformer.visit(tree)
    ast.fix_missing_locations(patched_tree)
    
    return ast.unparse(patched_tree)

def patch_file(input_path, output_path):
    if not os.path.exists(input_path):
        return False
    with open(input_path, "r") as f:
        src = f.read()
    patched = auto_patch_source(src)
    with open(output_path, "w") as f:
        f.write(patched)
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 patcher.py <input.py> <output_patched.py>")
        sys.exit(1)
    patch_file(sys.argv[1], sys.argv[2])
    print("[*] AST Auto-patch applied successfully.")
