# Python Dependencies Generator

A simple tool to automatically detect Python project dependencies and generate requirements.txt. It analyzes your Python files recursively, detects imports, and handles common package name mappings (like 'yaml' → 'PyYAML').

## Installation

```bash
pip install python-deps-generator
pip install .

```

## Usage

From the command line:
```bash
generate-deps
```

This will:
1. Scan all Python files in the current directory and subdirectories
2. Detect third-party imports
3. Map import names to correct package names (e.g., 'yaml' → 'PyYAML')
4. Generate a requirements.txt file

## Features

- Recursive scanning of Python files
- Automatic detection of third-party imports
- Mapping of common import names to correct package names
- Filtering out standard library modules
- Detection of local modules (to exclude them)

## Common Package Mappings

The tool handles many common package name mappings, including:
- `yaml` → `PyYAML`
- `dotenv` → `python-dotenv`
- `PIL` → `Pillow`
- `sklearn` → `scikit-learn`
- And many more...

## As a Python Module

You can also use it in your Python code:

```python
from python_deps_generator import generate_requirements

# Generate requirements.txt in current directory
generate_requirements()

# Or specify a directory
generate_requirements("/path/to/project")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.