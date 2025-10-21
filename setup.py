"""
Setup script per FlukeReader.
"""

from setuptools import setup, find_packages

# Legge il contenuto del README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Legge i requisiti
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fluke-thermal-reader",
    version="0.1.0",
    author="Lorenzo Ghidini",
    author_email="lorigh46@gmail.com",
    description="Libreria Python per leggere file termografici Fluke (.is2 e .is3)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LoriGH25/FlukeReader_Python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
    entry_points={
        "console_scripts": [
            "fluke-reader=fluke_reader.cli:main",
        ],
    },
)
