PYTHON  := python3
PIP     := $(PYTHON) -m pip
MAIN    := pac-man.py
CONFIG  := config.json

MYPY_FLAGS := --warn-return-any --warn-unused-ignores \
              --ignore-missing-imports --disallow-untyped-defs \
              --check-untyped-defs

.PHONY: install run debug clean lint lint-strict



install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install ./mazegenerator-2.1.0-py3-none-any.whl

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

lint:
	flake8 .
	mypy . $(MYPY_FLAGS)

lint-strict:
	flake8 .
	mypy . --strict


clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache build dist *.spec
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete
