# scenario-id: US-04/SC-5
"""AC-5: app.py imports only stdlib modules."""

import ast
import json
import pathlib

# Use AST to verify no third-party imports exist in app.py
source = pathlib.Path("app.py").read_text()
tree = ast.parse(source)

STDLIB_MODULES = {
    "json", "sys", "threading", "http", "socketserver",
    "os", "re", "io", "time", "datetime", "collections",
    "functools", "itertools", "pathlib", "typing",
    "urllib", "email", "html", "string", "struct",
    "hashlib", "hmac", "base64", "uuid", "logging",
    "traceback", "contextlib", "abc", "copy", "math",
}

non_stdlib = []
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            top = alias.name.split(".")[0]
            if top not in STDLIB_MODULES:
                non_stdlib.append(top)
    elif isinstance(node, ast.ImportFrom):
        if node.module:
            top = node.module.split(".")[0]
            if top not in STDLIB_MODULES:
                non_stdlib.append(top)

exit_code = 0 if not non_stdlib else 1

print(json.dumps({
    "exit_code": exit_code,
    "non_stdlib_imports": non_stdlib,
}))
