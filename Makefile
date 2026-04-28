PYTHON := .venv/bin/python
PIP := .venv/bin/pip
VENV := .venv
MAIN := main.py
MAP ?= maps/easy/01_linear_path.txt

.PHONY: install run debug clean lint lint-strict

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install pygame

run:
	$(PYTHON) $(MAIN) $(MAP)

debug:
	$(PYTHON) -m pdb $(MAIN) $(MAP)

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache .ruff_cache
	rm -rf $(VENV)

lint:
	flake8 --exclude=.venv .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 --exclude=.venv .
	mypy . --strict
