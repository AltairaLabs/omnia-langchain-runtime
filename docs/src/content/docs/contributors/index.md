---
title: Contributing
description: How to contribute to the Omnia LangChain Runtime
sidebar:
  order: 0
---

We welcome contributions to the Omnia LangChain Runtime!

## Development Setup

1. Clone the repository:

```bash
git clone https://github.com/AltairaLabs/omnia-langchain-runtime.git
cd omnia-langchain-runtime
```

2. Install development dependencies:

```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Code Quality

### Linting

```bash
ruff check src tests
```

### Formatting

```bash
ruff format src tests
```

### Type Checking

```bash
mypy src
```

## Generating gRPC Code

After modifying the proto files:

```bash
python -m grpc_tools.protoc -I proto \
    --python_out=src/omnia_langchain_runtime \
    --grpc_python_out=src/omnia_langchain_runtime \
    proto/runtime.proto
```

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for public APIs
- Keep functions focused and small

## Documentation

Documentation is built with Astro and Starlight:

```bash
cd docs
npm install
npm run dev
```
