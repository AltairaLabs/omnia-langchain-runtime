# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

.PHONY: all build test lint format proto docker clean help

# Variables
PYTHON := python3
PIP := pip
IMAGE_NAME := omnia-langchain-runtime
IMAGE_TAG := latest

all: lint test build

# Install development dependencies
install-dev:
	$(PIP) install -e ".[dev]"

# Install with all extras
install-all:
	$(PIP) install -e ".[all]"

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=src/omnia_langchain_runtime --cov-report=term-missing

# Lint code
lint:
	ruff check src tests

# Format code
format:
	ruff format src tests

# Type check
typecheck:
	mypy src

# Generate protobuf code (requires grpcio-tools)
proto:
	$(PYTHON) -m grpc_tools.protoc \
		-I proto \
		--python_out=src/omnia_langchain_runtime \
		--grpc_python_out=src/omnia_langchain_runtime \
		proto/runtime.proto

# Build Docker image
docker:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

# Run locally with mock provider
run-mock:
	OMNIA_AGENT_NAME=test \
	OMNIA_NAMESPACE=default \
	OMNIA_PROVIDER_TYPE=mock \
	OMNIA_PROMPTPACK_PATH=tests/fixtures/test.pack.json \
	$(PYTHON) -m omnia_langchain_runtime

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Help
help:
	@echo "Available targets:"
	@echo "  install-dev    Install development dependencies"
	@echo "  install-all    Install with all extras"
	@echo "  test           Run tests"
	@echo "  test-cov       Run tests with coverage"
	@echo "  lint           Run linter"
	@echo "  format         Format code"
	@echo "  typecheck      Run type checker"
	@echo "  proto          Generate protobuf code"
	@echo "  docker         Build Docker image"
	@echo "  run-mock       Run locally with mock provider"
	@echo "  clean          Clean build artifacts"
