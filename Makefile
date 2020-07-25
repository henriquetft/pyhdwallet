# Makefile for pyhdutils

.PHONY: test lint coverage

PACKAGE=pyhdutils
RUNTEST=python -m unittest -b -v

test:
	${RUNTEST}

lint:
	pylint --disable=R0913,C0103 ${PACKAGE}

coverage:
	coverage run -m unittest
	coverage report -m
