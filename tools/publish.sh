#!/usr/bin/bash

PYTHON=python3.9

echo starting.. \
	&& rm ../setup.py \
	&& cp setup.py ..  \
	&& cd ..  \
	&& $PYTHON -m pip install build twine \
	&& rm -rf dist \
	&& $PYTHON -m build \
	&& $PYTHON -m twine upload dist/*  --verbose

