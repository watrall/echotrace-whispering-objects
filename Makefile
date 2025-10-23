PYTHON ?= python3

.PHONY: install lint typecheck test run-hub run-node

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

lint:
	ruff check .
	flake8

typecheck:
	mypy .

test:
	pytest

run-hub:
	$(PYTHON) -m hub.dashboard_app

run-node:
	$(PYTHON) -m pi_nodes.node_service
