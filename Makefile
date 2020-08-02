# Makefile for pyhdwallet

PACKAGE=pyhdwallet
RUNTEST=python -m unittest -b -v

.PHONY: test lint coverage help

.DEFAULT: help

help:
	@echo "Make targets for pyhdwallet:"
	@echo
	@echo "make test"
	@echo "       run tests"
	@echo "make coverage"
	@echo "       run tests and show coverage report"
	@echo "make lint"
	@echo "       run pylint"

test:
	${RUNTEST}

lint:
	pylint --disable=R0913,C0103 ${PACKAGE}

coverage:
	coverage run -m unittest
	coverage report -m
