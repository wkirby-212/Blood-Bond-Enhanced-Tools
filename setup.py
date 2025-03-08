import os
import re
from setuptools import setup, find_packages

# Read version from __init__.py
with open('bloodbond/__init__.py', 'r') as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    version = version_match.group(1) if version_match else '0.1.0'

# Read README.md content for long description
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Blood Bond Enhanced Tools - A Python implementation of tools for the Blood Bond TTRPG system"

# Get list of data files
def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            # Include all data files, not just JSON
            if any(filename.endswith(ext) for ext in ['.json', '.txt', '.csv', '.yaml', '.yml']):
                # Adjust path for proper inclusion in the package
                rel_path = os.path.relpath(os.path.join(path, filename), 'bloodbond')
                paths.append(os.path.join('..', rel_path))
    return paths

# Include bloodbond data files
bloodbond_data_files = package_files('bloodbond/data')

# Include root data directory files
root_data_files = []
if os.path.exists('data'):
    for (path, directories, filenames) in os.walk('data'):
        for filename in filenames:
            if any(filename.endswith(ext) for ext in ['.json', '.txt', '.csv', '.yaml', '.yml']):
                # Store path relative to package root
                root_data_files.append(os.path.join('..', '..', path, filename))

setup(
    name="bloodbond-enhanced-tools",
    version=version,
    author="Blood Bond Development Team",
    author_email="contact@bloodbond.example.com",
    description="Enhanced tools for creating and managing spells in the Blood Bond TTRPG system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bloodbond/enhanced-tools",
    packages=find_packages(),
    package_data={
        'bloodbond': bloodbond_data_files + root_data_files,
    },
    include_package_data=True,
    install_requires=[
        'customtkinter>=5.2.0',
        'pillow>=10.0.0',
        'pandas>=2.0.3',
        'pyyaml>=6.0.1',
        'jsonschema>=4.19.0',
        'rapidfuzz>=3.2.0',
        'nltk>=3.8.1',
        'tqdm>=4.66.1',
        'colorama>=0.4.6',
        'python-dotenv>=1.0.0',
        'ttkthemes',
        'pyperclip',
        'rich',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Role-Playing",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'bloodbond-cli=bloodbond.main:start_cli',
        ],
        'gui_scripts': [
            'bloodbond-gui=bloodbond.main:start_gui',
        ],
    },
)

