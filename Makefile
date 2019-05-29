all:

test: tests

tests:
	python -m pytest -vvs --cov=can2mqtt --cov-report=term-missing

bdist_wheel:
	python setup.py bdist_wheel

build: bdist_wheel

.PHONY: all tests
