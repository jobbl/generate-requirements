import ast
import os
import sys
from pathlib import Path

# Common package name mappings
PACKAGE_MAPPINGS = {
    # Data Science & ML
    'sklearn': 'scikit-learn',
    'PIL': 'Pillow',
    'cv2': 'opencv-python',
    'np': 'numpy',
    'pd': 'pandas',
    'plt': 'matplotlib',
    'tf': 'tensorflow',
    'torch': 'torch',
    
    # Web & APIs
    'bs4': 'beautifulsoup4',
    'flask_cors': 'Flask-Cors',
    'flask_sqlalchemy': 'Flask-SQLAlchemy',
    'flask': 'Flask',
    'jwt': 'PyJWT',
    
    # Utils & Config
    'dotenv': 'python-dotenv',
    'yaml': 'PyYAML',
    'toml': 'toml',
    
    # Database
    'psycopg2': 'psycopg2-binary',
    'pymongo': 'pymongo',
    'sqlalchemy': 'SQLAlchemy',
}

class ImportFinder(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name.split('.')[0])
    
    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module.split('.')[0])

def find_imports_in_file(file_path):
    """Find all imports in a Python file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read())
            finder = ImportFinder()
            finder.visit(tree)
            return finder.imports
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            return set()

def is_stdlib_module(module_name):
    """Check if a module is part of the Python standard library."""
    stdlib_modules = {
        'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections', 'configparser', 
        'copy', 'csv', 'datetime', 'decimal', 'email', 'enum', 'functools', 'glob', 
        'hashlib', 'hmac', 'html', 'http', 'importlib', 'inspect', 'io', 'itertools', 
        'json', 'logging', 'math', 'multiprocessing', 'os', 'pathlib', 'pickle', 
        'platform', 'queue', 're', 'shutil', 'signal', 'socket', 'sqlite3', 'string', 
        'subprocess', 'sys', 'tempfile', 'threading', 'time', 'traceback', 'types', 
        'typing', 'unittest', 'urllib', 'uuid', 'warnings', 'weakref', 'xml', 'zipfile'
    }
    
    return (module_name in stdlib_modules or
            (hasattr(sys, 'stdlib_module_names') and module_name in sys.stdlib_module_names))

def find_project_dependencies(project_path):
    """Find all third-party dependencies in a Python project."""
    all_imports = set()
    
    # Walk through all Python files in the project
    for path in Path(project_path).rglob('*.py'):
        # Skip the generator script itself
        if path.name != 'generate_requirements.py':
            imports = find_imports_in_file(path)
            all_imports.update(imports)
    
    # Filter out standard library modules and local imports
    third_party_imports = {
        imp for imp in all_imports 
        if not is_stdlib_module(imp) and not imp.startswith('.')
        and not os.path.exists(os.path.join(project_path, f"{imp}.py"))
    }
    
    return third_party_imports

def write_requirements(dependencies, filename='requirements.txt'):
    """Write dependencies to requirements.txt."""
    requirements = []
    
    # Map package names
    for dep in dependencies:
        pkg_name = PACKAGE_MAPPINGS.get(dep, dep)
        requirements.append(pkg_name)
    
    # Write to file
    with open(filename, 'w') as f:
        for req in sorted(requirements):
            f.write(f"{req}\n")

def generate_requirements(project_path=None):
    """Main function to generate requirements.txt."""
    if project_path is None:
        project_path = os.getcwd()
    
    print("Analyzing Python files for dependencies...")
    dependencies = find_project_dependencies(project_path)
    
    if not dependencies:
        print("No third-party dependencies found.")
        return
    
    print("\nFound the following third-party imports:")
    for dep in sorted(dependencies):
        mapped_name = PACKAGE_MAPPINGS.get(dep, dep)
        if mapped_name != dep:
            print(f"- {dep} (will use package: {mapped_name})")
        else:
            print(f"- {dep}")
    
    write_requirements(dependencies)
    
    print("\nrequirements.txt has been created!")
    print("You can install the dependencies using:")
    print("pip install -r requirements.txt")

def main():
    """CLI entry point."""
    import argparse
    parser = argparse.ArgumentParser(description='Generate requirements.txt from Python project imports.')
    parser.add_argument('--path', type=str, default=None, 
                       help='Path to the Python project (default: current directory)')
    args = parser.parse_args()
    
    generate_requirements(args.path)

if __name__ == "__main__":
    main()