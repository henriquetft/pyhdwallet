# Makefile for pyhdwallet

# tools
PYTHON=python
PYLINT=${PYTHON} -m pylint
COVERAGE=coverage

PROJECT=pyhdwallet

.PHONY: help test coverage lint clean docs dist upload-test upload deps install

.DEFAULT: help

help:
	@echo "Make targets for ${PROJECT}:"
	@echo
	@echo "make help"
	@echo "       print this help"
	@echo "make test"
	@echo "       run tests"
	@echo "make coverage"
	@echo "       run tests and show coverage report"
	@echo "make lint"
	@echo "       run pylint"
	@echo "make clean"
	@echo "       clean project"
	@echo "make docs"
	@echo "       generate project docs"
	@echo "make dist"
	@echo "       generate distribution packages"
	@echo "make upload-test"
	@echo "       upload testpypi"
	@echo "make upload"
	@echo "       upload pypi"
	@echo "make deps"
	@echo "       install the list of requirements"
	@echo "make install"
	@echo "       install ${PROJECT}"

test:
	${PYTHON} -m unittest -b -v

lint:
	${PYLINT} --disable=R0913,C0103 ${PROJECT}

coverage:
	${COVERAGE} run -m unittest
	${COVERAGE} report -m


clean:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -f .coverage

docs:
	rm -f sphinx/modules.rst
	rm -f sphinx/pyhdwallet.rst
	make -C sphinx clean
	sphinx-apidoc -o ./sphinx . ./tests/* ./setup.py
	make -C sphinx html
	rm -rf ./docs
	mv ./sphinx/_build/html/ ./docs
	touch ./docs/.nojekyll

dist: clean lint test docs
	${PYTHON} setup.py sdist
	${PYTHON} setup.py bdist_wheel
	ls -l dist

deps:
	@echo "Installing requirements for ${PROJECT} ..."
	${PYTHON} -m pip install -r requirements.txt

upload-test: dist
	${PYTHON} -m twine upload --repository testpypi dist/*

install: deps dist
	${PYTHON} setup.py install

upload: dist
	${PYTHON} -m twine upload dist/*
