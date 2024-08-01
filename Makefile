MAKEFLAGS += --warn-undefined-variables
MICRO_MAMBA := $(CURDIR)/.micromamba
MAMBA := $(MICRO_MAMBA)/micromamba
SHELL := $(shell which bash) -o pipefail
VENV := $(CURDIR)/venv
DEPS := $(VENV)/.deps
VENV_BIN := $(VENV)/bin
PYTHON := $(VENV)/bin/python
PYTHON_CMD := PYTHONPATH=$(shell pwd) $(PYTHON)
PLATFORM=$(shell uname | tr '[:upper:]' '[:lower:]' | sed 's/darwin/osx/g')
ARCH := $(shell uname -m | sed 's/x86_64/64/g')

.PHONY: help
help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

ifndef VERBOSE
.SILENT:
endif

FORCE:

$(MAMBA):
	echo "Installing Mamba..."
	mkdir -p "$(MICRO_MAMBA)"
	curl -Ls https://micro.mamba.pm/api/micromamba/$(PLATFORM)-$(ARCH)/1.5.8 | tar -xj -C "$(MICRO_MAMBA)" --strip-components=1 bin/micromamba

$(PYTHON): | $(MAMBA)
	echo "Installing Python..."
	$(MAMBA) create --quiet --yes -p $(VENV)

$(DEPS): environment.yml $(PYTHON)
	echo "Installing dependencies..."
	rm -rf $(VENV)
	$(MAMBA) create --quiet --yes -p $(VENV)
	$(MAMBA) install --quiet --yes -p $(VENV) -f environment.yml
	cp environment.yml $(DEPS)

.PHONY: clean
clean:
	rm -rf $(MICRO_MAMBA)
	rm -rf $(VENV)
	find . -name __pycache__ | xargs --no-run-if-empty rm -rf

.PHONY: pytest
pytest: deps
	$(PYTHON_CMD) -m pytest -vv --ignore $(VENV)

.PHONY: mypy
mypy: deps
	$(PYTHON_CMD) -m mypy interview

.PHONY: pylint
pylint: deps
	$(PYTHON_CMD) -m pylint interview

.PHONY: deps
deps: $(DEPS)

.PHONY: test
test: pytest pylint mypy ## run unit tests and linters

.PHONY: coverage
coverage: deps
	$(VENV)/bin/pytest --cov-report html:reports --cov=interview interview/

.PHONY: build
build: coverage test

.PHONY: watch
watch: deps ## run unit tests continuously
	$(PYTHON_CMD) -m pytest_watcher --ignore-patterns "$(VENV)/*" --now --runner $(VENV_BIN)/pytest interview
