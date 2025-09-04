from setuptools import setup, find_packages

setup(
    name="ccc_clock",
    version="1.0.0",
    packages=find_packages(),
    description="Computational Complexity Cosmology (CCC) Clock Demonstration System",
    long_description="A complete implementation of CCC theory for demonstrating information-induced time dilation in optical clocks.",
    author="CCC Clock Development Team",
    author_email="contact@ccc-clock.org",
    url="https://github.com/Tnsr-Q/ccc_clock",
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "pandas>=1.3.0",
        "plotly>=5.0.0",
        "ipywidgets>=7.6.0",
        "jupyter>=1.0.0",
        "notebook>=6.4.0",
        "nbconvert>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "isort>=5.0.0",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
            "myst-parser>=0.15.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
