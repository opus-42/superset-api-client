from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="superset-api-client",
    version="0.1.0",
    description=("A simple REST Api Client for Apache-Superset"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    author="Emmanuel B.",
    install_requires=[
        "requests"
    ],
    extras_require={
        "dev": [
            "pytest",
            "apache-superset==1.0.1"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha"
    ]
)
