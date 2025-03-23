import time
from config import JsonConfig
from path import Path
import ast
import os
import venv
import sys
import subprocess

CONFIG = "chocolate.json"
p = Path()


def get_config():
    """Receiving config from the path"""
    if CONFIG in p:
        return JsonConfig(CONFIG)
    return False


def setup_project(name, start):
    """Setting up the project"""
    p[CONFIG] = {
        "info": {
            "fork": "native",
            "createdUnix": round(time.time()),
            "name": name
        },
        "requirements": list(),
        "startupEnv": list(),
        "privateEnv": list(),
        "exclude": list(),
        "mainFile": start,
        "flagsString": "",
        "environmentVariables": dict(),
        "actionsScript": dict()
    }
    if not os.path.exists(start):
        with open(start, '+wt', encoding='utf-8') as fp:
            fp.write('print("Hello, Chocolate!")')


class VenvManager:
    def __init__(self, venv_dir="venv"):
        self.venv_dir = venv_dir
        self.venv_python = os.path.join(venv_dir, "bin", "python") if os.name != "nt" else os.path.join(
            venv_dir, "Scripts", "python.exe")

        # Create the virtual environment if it doesn't exist
        if not os.path.exists(venv_dir):
            print(f"Creating virtual environment at {venv_dir}...")
            venv.create(venv_dir, with_pip=True)

    def install(self, package_name):
        """Install a package inside the virtual environment."""
        subprocess.run([self.venv_python, "-m", "pip",
                       "install", package_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def run(self, file_name, flags="", env={}):
        """Run a script inside the virtual environment with optional flags."""
        command = [self.venv_python, file_name] + flags.split()
        return subprocess.run(command, check=True, env=env).returncode
    
    def run_sandbox(self, file_name, flags="", env={}, memory=-1, cpu_time=-1, freq=-1):
        command = [self.venv_python, file_name ] + flags.split()
        command = " ".join(command)
        command = ["sudo", "choco-sandbox", command, memory, cpu_time, freq]
        return subprocess.run(command, check=True, env=env).returncode
    


def find_python_files(directory):
    """Recursively find all Python files in a directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files


def extract_imports(file_path):
    """Extract imports from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read())
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)

    return imports


def collect_imports(directory):
    """Collect all unique imports from Python files in a directory."""
    python_files = find_python_files(directory)
    all_imports = set()

    for file_path in python_files:
        imports = extract_imports(file_path)
        all_imports.update(imports)

    return all_imports


def get_builtin_libraries():
    """Return a set of built-in libraries."""
    return set(sys.builtin_module_names)


def export_non_builtin_imports(imports, output_file):
    """Export only non-builtin imports to a file, filtering out None values."""
    # Get the set of built-in libraries
    builtin_libraries = get_builtin_libraries()

    # Filter out built-in libraries and None values from the imports
    non_builtin_imports = {
        imp for imp in imports if imp not in builtin_libraries and imp is not None}

    # Write the remaining non-builtin imports to the file
    with open(output_file, 'w', encoding='utf-8') as file:
        for imp in sorted(non_builtin_imports):
            file.write(f"{imp}\n")


def exporter(directory, output_file):
    imports = collect_imports(directory)
    export_non_builtin_imports(imports, output_file)
    print(f"Exported non-builtin imports to {output_file}")


