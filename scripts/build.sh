#!/bin/bash

python -m pip install --upgrade setuptools build
python -m build .

python -m pip install --upgrade twine
python -m twine upload dist/*
