# Makefile for NetDoctor

.PHONY: venv install test run lint clean help

# Default shell
SHELL := /bin/bash

# Configuration
PYTHON := python
VENV := venv
BIN := $(VENV)/Scripts
ifeq ($(OS),Windows_NT)
    PYTHON_VENV := $(VENV)/Scripts/python
    PIP_VENV := $(VENV)/Scripts/pip
    PYTEST_VENV := $(VENV)/Scripts/pytest
else
    PYTHON_VENV := $(VENV)/bin/python
    PIP_VENV := $(VENV)/bin/pip
    PYTEST_VENV := $(VENV)/bin/pytest
endif

help:
	@echo "Available commands:"
	@echo "  make venv     : Create a virtual environment"
	@echo "  make install  : Install dependencies"
	@echo "  make test     : Run tests"
	@echo "  make run      : Run the application"
	@echo "  make lint     : Run linting (black, ruff, mypy)"
	@echo "  make clean    : Remove build and cache files"

venv:
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created in $(VENV)"

install: venv
	$(PIP_VENV) install --upgrade pip
	$(PIP_VENV) install -r requirements.txt
	$(PIP_VENV) install black ruff mypy pytest pytest-qt pre-commit
	$(PYTHON_VENV) -m pre_commit install

test:
	$(PYTEST_VENV)

run:
	$(PYTHON_VENV) -m netdoctor.main

lint:
	$(PYTHON_VENV) -m black .
	$(PYTHON_VENV) -m ruff check .
	$(PYTHON_VENV) -m mypy .

clean:
	rm -rf build/ dist/ *.spec .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
