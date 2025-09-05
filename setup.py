from setuptools import setup, find_packages
import os

# Read requirements from the requirements.txt file
def read_requirements():
    req_path = os.path.join("ccc_clock", "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="ccc_clock",
    version="0.1.0",
    package_dir={"": "ccc_clock"},
    packages=find_packages(where="ccc_clock"),
    install_requires=read_requirements(),
    description="CCC Clock Demonstration System - Computational Complexity Cosmology implementation",
    author="CCC Clock Team",
    author_email="ccc@example.com",
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10", 
        "Programming Language :: Python :: 3.11",
    ],
)
