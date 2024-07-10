MAKEFLAGS += --warn-undefined-variables
MICRO_MAMBA := $(CURDIR)/.micromamba
MAMBA := $(MICRO_MAMBA)/micromamba
SHELL := $(shell which bash) -o pipefail
VENV := $(CURDIR)/.venv
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
	curl -Ls https://micro.mamba.pm/api/micromamba/$(PLATFORM)-$(ARCH)/latest | tar -xj -C "$(MICRO_MAMBA)" --strip-components=1 bin/micromamba

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
clean: ## Remove virtual environment and caches
	rm -rf $(MICRO_MAMBA)
	rm -rf $(VENV)
	find . -name __pycache__ | xargs --no-run-if-empty rm -rf

.PHONY: deps
deps: $(DEPS)  ## install the project dependencies

.PHONY: test
test: deps ## run all the test type things
	$(PYTHON_CMD) -m pytest --ignore $(VENV)

.PHONY: watch
watch: deps ## run unit tests in a continuous loop
	$(PYTHON_CMD) -m pytest_watch --runner $(VENV_BIN)/pytest --ignore $(VENV)
