"""
docs-from-code — Python Code Extractor
Uses Python's built-in `ast` module to extract structured metadata.
Works for Flask, FastAPI, Django REST, and plain Python projects.

Usage: python extract_py.py <project-root> [output-file]
"""

import ast
import json
import os
import sys
from pathlib import Path
from typing import Any


def get_docstring(node: ast.AST) -> str:
    """Extract docstring from a function, class, or module node."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
        if (node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value.strip()
    return ""


def get_annotation(node: Any) -> str:
    """Convert AST annotation to string."""
    if node is None:
        return ""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        return str(node.value)
    if isinstance(node, ast.Attribute):
        return f"{get_annotation(node.value)}.{node.attr}"
    if isinstance(node, ast.Subscript):
        return f"{get_annotation(node.value)}[{get_annotation(node.slice)}]"
    if isinstance(node, ast.Tuple):
        return ", ".join(get_annotation(e) for e in node.elts)
    if isinstance(node, ast.BinOp):
        return f"{get_annotation(node.left)} | {get_annotation(node.right)}"
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def extract_functions(tree: ast.Module, file_path: str, is_exported_only: bool = False):
    """Extract top-level functions and their signatures."""
    functions = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.col_offset != 0:  # skip nested functions / methods
            continue
        if is_exported_only and node.name.startswith("_"):
            continue

        args = node.args
        params = []
        all_args = args.posonlyargs + args.args + args.kwonlyargs
        for i, arg in enumerate(all_args):
            params.append({
                "name": arg.arg,
                "type": get_annotation(arg.annotation),
                "description": ""
            })

        returns = get_annotation(node.returns)
        is_async = isinstance(node, ast.AsyncFunctionDef)

        functions.append({
            "name": node.name,
            "signature": f"{'async ' if is_async else ''}def {node.name}({', '.join(p['name'] + (': ' + p['type'] if p['type'] else '') for p in params)}) -> {returns}",
            "description": get_docstring(node),
            "params": params,
            "returns": returns,
            "file": file_path,
            "isExported": not node.name.startswith("_")
        })
    return functions


def extract_routes(tree: ast.Module, file_path: str, framework: str):
    """Extract API routes from FastAPI, Flask, or Django decorators."""
    routes = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        for decorator in node.decorator_list:
            # FastAPI / Flask style: @app.get("/path") or @router.post("/path")
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                method = decorator.func.attr.upper()
                if method in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]:
                    route_path = ""
                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                        route_path = decorator.args[0].value
                    routes.append({
                        "method": method,
                        "path": route_path,
                        "handler": node.name,
                        "description": get_docstring(node),
                        "file": file_path
                    })

            # Django REST: @api_view(['GET', 'POST'])
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == "api_view":
                    for arg in decorator.args:
                        if isinstance(arg, ast.List):
                            for elt in arg.elts:
                                if isinstance(elt, ast.Constant):
                                    routes.append({
                                        "method": elt.value,
                                        "path": "",
                                        "handler": node.name,
                                        "description": get_docstring(node),
                                        "file": file_path
                                    })

    return routes


def extract_classes(tree: ast.Module, file_path: str):
    """Extract class definitions with their public methods."""
    classes = []
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        methods = []
        for item in ast.iter_child_nodes(node):
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not item.name.startswith("__"):
                    methods.append(item.name)
        classes.append({
            "name": node.name,
            "kind": "class",
            "definition": f"class {node.name}",
            "description": get_docstring(node),
            "methods": methods,
            "file": file_path
        })
    return classes


def detect_framework(project_root: str) -> str:
    """Detect Python framework from requirements.txt or pyproject.toml."""
    req_files = [
        os.path.join(project_root, "requirements.txt"),
        os.path.join(project_root, "requirements/base.txt"),
    ]
    for req_file in req_files:
        if os.path.exists(req_file):
            content = open(req_file).read().lower()
            if "fastapi" in content:
                return "fastapi"
            if "flask" in content:
                return "flask"
            if "django" in content:
                return "django"
            if "tornado" in content:
                return "tornado"

    pyproject = os.path.join(project_root, "pyproject.toml")
    if os.path.exists(pyproject):
        content = open(pyproject).read().lower()
        if "fastapi" in content:
            return "fastapi"
        if "flask" in content:
            return "flask"
        if "django" in content:
            return "django"

    return "python"


def main():
    project_root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    output_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(project_root, ".docs-extract.json")

    framework = detect_framework(project_root)
    skip_dirs = {"__pycache__", ".git", "node_modules", "venv", ".venv", "env",
                 "dist", "build", ".tox", "migrations", "static", "media"}

    metadata = {
        "projectName": os.path.basename(project_root),
        "language": "python",
        "framework": framework,
        "entryPoints": [],
        "functions": [],
        "routes": [],
        "types": [],
        "dependencies": {},
        "scripts": {}
    }

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]
        for file in files:
            if not file.endswith(".py"):
                continue
            file_path = os.path.join(root, file)
            try:
                source = open(file_path, encoding="utf-8").read()
                tree = ast.parse(source, filename=file_path)
            except (SyntaxError, UnicodeDecodeError):
                continue

            metadata["functions"].extend(extract_functions(tree, file_path, is_exported_only=True))
            metadata["routes"].extend(extract_routes(tree, file_path, framework))
            metadata["types"].extend(extract_classes(tree, file_path))

    # Detect entry points
    for candidate in ["main.py", "app.py", "server.py", "manage.py", "run.py", "wsgi.py"]:
        if os.path.exists(os.path.join(project_root, candidate)):
            metadata["entryPoints"].append(candidate)

    # Read requirements
    req_file = os.path.join(project_root, "requirements.txt")
    if os.path.exists(req_file):
        for line in open(req_file):
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split("==")
                metadata["dependencies"][parts[0]] = parts[1] if len(parts) > 1 else "*"

    with open(output_file, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Extracted {len(metadata['functions'])} functions, {len(metadata['routes'])} routes, {len(metadata['types'])} classes")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
