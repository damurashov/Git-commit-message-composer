#!/usr/bin/bash

PYTHON=python3.9

if [ -z $VERSION ] ; then
	echo VERSION env. must be specified!
	exit 1
fi

replaceinfiles.py 'setup.py' '@VERSION@' $VERSION

echo starting.. \
	&& rm ../setup.py \
	&& cp setup.py ..  \
	&& cd ..  \
	&& $PYTHON -m pip install build twine \
	&& rm -rf dist \
	&& $PYTHON -m build \
	&& $PYTHON -m twine upload dist/*  --verbose

