import ast
import os
import sys
import importlib.util
from pathlib import Path
import subprocess

# Common package name mappings
PACKAGE_MAPPINGS = {
    # Data Science & Machine Learning
    'sklearn': 'scikit-learn',
    'PIL': 'Pillow',
    'cv2': 'opencv-python',
    'tensorflow.keras': 'tensorflow',
    'keras': 'keras',
    'nx': 'networkx',
    'pd': 'pandas',
    'np': 'numpy',
    'plt': 'matplotlib',
    'scipy.sparse': 'scipy',
    'scipy.stats': 'scipy',
    'scipy.optimize': 'scipy',
    'scipy': 'scipy',
    'skimage': 'scikit-image',
    'tf': 'tensorflow',
    'torch.cuda': 'torch',
    'torch.nn': 'torch',
    'torch.utils': 'torch',
    'torch': 'torch',
    'xgboost': 'xgboost',
    'lightgbm': 'lightgbm',
    
    # Web Development
    'bs4': 'beautifulsoup4',
    'flask_cors': 'Flask-Cors',
    'flask_sqlalchemy': 'Flask-SQLAlchemy',
    'flask': 'Flask',
    'jwt': 'PyJWT',
    'redis': 'redis-py',
    'graphene': 'graphene-python',
    'requests_oauthlib': 'requests-oauthlib',
    
    # Database
    'psycopg2': 'psycopg2-binary',
    'pymongo': 'pymongo',
    'sqlalchemy': 'SQLAlchemy',
    
    # Utils & Config
    'dotenv': 'python-dotenv',
    'yaml': 'pyyaml',
    'ruamel.yaml': 'ruamel.yaml',
    'toml': 'toml',
    'conf': 'python-configuration',
    
    # CLI & System
    'click': 'click',
    'typer': 'typer',
    'rich': 'rich',
    'colorama': 'colorama',
    'pypdf2': 'PyPDF2',
    'pypdf': 'pypdf',
    
    # Testing
    'pytest': 'pytest',
    'nose': 'nose',
    'mock': 'mock',
    
    # AWS
    'boto3': 'boto3',
    'botocore': 'botocore',
    'awscli': 'awscli',
    
    # Azure
    'azure.storage': 'azure-storage-blob',
    'azure.cognitiveservices': 'azure-cognitiveservices-vision-computervision',
    
    # Google Cloud
    'google.cloud': 'google-cloud',
    'google.oauth2': 'google-auth',
    
    # Date & Time
    'dateutil': 'python-dateutil',
    'pytz': 'pytz',
    'pendulum': 'pendulum',
    
    # Async
    'aiohttp': 'aiohttp',
    'asyncio': 'asyncio',
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    
    # Image Processing
    'imageio': 'imageio',
    'wand': 'Wand',
    
    # Natural Language Processing
    'nltk': 'nltk',
    'spacy': 'spacy',
    'gensim': 'gensim',
    'transformers': 'transformers',
    
    # Documentation
    'sphinx': 'Sphinx',
    'mkdocs': 'mkdocs',
    
    # Serialization
    'msgpack': 'msgpack-python',
    'protobuf': 'protobuf',
    
    # Optimization
    'pulp': 'PuLP',
    'cvxopt': 'cvxopt',
    
    # Audio Processing
    'librosa': 'librosa',
    'soundfile': 'SoundFile',
    
    # Email
    'email_validator': 'email-validator',
    'smtplib': 'secure-smtplib',
    
    # Cryptography & Security
    'bcrypt': 'bcrypt',
    'cryptography': 'cryptography',
    
    # Progress Bars & CLI UI
    'tqdm': 'tqdm',
    'progressbar': 'progressbar2',
    
    # Code Quality & Formatting
    'black': 'black',
    'flake8': 'flake8',
    'pylint': 'pylint',
    'mypy': 'mypy',
    
    # Data Validation
    'pydantic': 'pydantic',
    'marshmallow': 'marshmallow',
    'cerberus': 'Cerberus',
    
    # API Development
    'connexion': 'connexion',
    'swagger_ui': 'swagger-ui-bundle',
    
    # Templating
    'jinja2': 'Jinja2',
    'mako': 'Mako',
    
    # Process & System
    'psutil': 'psutil',
    'watchdog': 'watchdog',
    
    # Scientific
    'sympy': 'sympy',
    'statsmodels': 'statsmodels',
    
    # Caching
    'cachetools': 'cachetools',
    'memcache': 'python-memcached',
    
    # Compression
    'zipfile': 'zipfile36',
    'gzip': 'gzip-reader',
    
    # GUI
    'tkinter': 'tk',
    'qt': 'PyQt5',
    'wx': 'wxPython',
    
    # Parsing
    'lxml': 'lxml',
    'feedparser': 'feedparser',
    'html5lib': 'html5lib',
}

class ImportFinder(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name.split('.')[0])
    
    def visit_ImportFrom(self, node):
        if node.module:
            base_module = node.module.split('.')[0]
            self.imports.add(base_module)

def find_imports_in_file(file_path):
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
    """More reliable standard library detection"""
    stdlib_packages = {
        'typing', 'os', 'sys', 'json', 'datetime', 'dataclasses', 
        'importlib', 'subprocess', 'traceback', 'collections', 'abc',
        'argparse', 'ast', 'base64', 'configparser', 'copy', 'csv',
        'enum', 'functools', 'glob', 'hashlib', 'hmac', 'io', 'inspect',
        'itertools', 'logging', 'math', 'operator', 'pathlib', 'pickle',
        're', 'shutil', 'signal', 'string', 'tempfile', 'time', 'types',
        'uuid', 'warnings', 'weakref', 'xml'
    }
    
    if module_name in stdlib_packages:
        return True
        
    if hasattr(sys, 'stdlib_module_names') and module_name in sys.stdlib_module_names:
        return True
    
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        
        # If it's in standard library paths
        stdlib_paths = [os.path.dirname(os.__file__)]
        return any(path.startswith(tuple(stdlib_paths)) for path in spec.submodule_search_locations or [spec.origin])
    except (ImportError, AttributeError):
        return False

def get_package_versions(packages):
    versions = {}
    try:
        output = subprocess.check_output(['pip', 'freeze'], text=True)
        pip_packages = {line.split('==')[0].lower(): line.strip() for line in output.split('\n') if line}
        
        for package in packages:
            # Map package name if necessary
            mapped_package = PACKAGE_MAPPINGS.get(package, package)
            package_lower = mapped_package.lower()
            
            if package_lower in pip_packages:
                versions[mapped_package] = pip_packages[package_lower]
            else:
                versions[mapped_package] = mapped_package
                
    except subprocess.CalledProcessError:
        for package in packages:
            mapped_package = PACKAGE_MAPPINGS.get(package, package)
            versions[mapped_package] = mapped_package
    
    return versions

def find_project_dependencies(project_path):
    all_imports = set()
    
    # Walk through all Python files in the project
    for path in Path(project_path).rglob('*.py'):
        imports = find_imports_in_file(path)
        all_imports.update(imports)
    
    # Filter out standard library modules and local imports
    third_party_imports = {
        imp for imp in all_imports 
        if not is_stdlib_module(imp) and not imp.startswith('.')
    }
    
    # Remove local module imports
    third_party_imports = {
        imp for imp in third_party_imports 
        if not os.path.exists(os.path.join(project_path, f"{imp}.py"))
    }
    
    return third_party_imports

def main():
    project_path = os.getcwd()
    
    print("Analyzing Python files for dependencies...")
    dependencies = find_project_dependencies(project_path)
    
    if not dependencies:
        print("No third-party dependencies found.")
        return
    
    print("\nFound the following third-party dependencies:")
    for dep in sorted(dependencies):
        mapped_name = PACKAGE_MAPPINGS.get(dep, dep)
        if mapped_name != dep:
            print(f"- {dep} (will use package: {mapped_name})")
        else:
            print(f"- {dep}")
    
    print("\nGetting installed versions...")
    versions = get_package_versions(dependencies)
    
    # Write requirements.txt
    with open('requirements.txt', 'w') as f:
        for package in sorted(versions.values()):
            f.write(f"{package}\n")
    
    print("\nrequirements.txt has been created!")
    print("You can install the dependencies using:")
    print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()