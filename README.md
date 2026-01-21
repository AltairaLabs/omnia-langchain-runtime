# Omnia LangChain Runtime

A Python-based LangChain runtime for Omnia that enables running LangChain agents while reusing the existing facade architecture and gRPC protocol.

## Overview

This runtime implements the Omnia runtime gRPC protocol, allowing LangChain-based agents to be deployed in Kubernetes alongside the existing Go-based runtime.

## Features

- **gRPC Protocol**: Implements the `omnia.runtime.v1.RuntimeService` protocol
- **LangChain Integration**: Uses LangChain and LangGraph for agent orchestration
- **Multiple Providers**: Supports Claude, OpenAI, Gemini, and Ollama
- **Session Management**: Memory and Redis session stores
- **Tool Support**: HTTP and MCP tool adapters
- **PromptPack Support**: Uses PromptPack for prompt configuration

## Installation

```bash
pip install omnia-langchain-runtime

# With Redis support
pip install omnia-langchain-runtime[redis]
```

## Configuration

The runtime is configured via environment variables:

```bash
# Required
OMNIA_AGENT_NAME=my-agent
OMNIA_NAMESPACE=default

# PromptPack
OMNIA_PROMPTPACK_PATH=/etc/omnia/pack/pack.json
OMNIA_PROMPT_NAME=default

# Provider
OMNIA_PROVIDER_TYPE=claude  # claude, openai, gemini, ollama, mock
OMNIA_PROVIDER_MODEL=claude-sonnet-4-20250514

# Session (optional)
OMNIA_SESSION_TYPE=memory  # memory or redis
OMNIA_SESSION_URL=redis://localhost:6379

# Tools (optional)
OMNIA_TOOLS_CONFIG=/etc/omnia/tools/tools.yaml

# Server ports
OMNIA_GRPC_PORT=9000
OMNIA_HEALTH_PORT=9001
```

## Usage

### Running the Server

```bash
# Using the CLI
omnia-langchain-runtime

# Or using Python module
python -m omnia_langchain_runtime
```

### Docker

```bash
docker build -t omnia-langchain-runtime .
docker run -e OMNIA_AGENT_NAME=test \
           -e OMNIA_NAMESPACE=default \
           -e OMNIA_PROVIDER_TYPE=mock \
           -p 9000:9000 \
           omnia-langchain-runtime
```

### Kubernetes

Deploy using the Omnia AgentRuntime CRD with `framework: langchain`.

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Generate gRPC code
python -m grpc_tools.protoc -I proto \
    --python_out=src/omnia_langchain_runtime \
    --grpc_python_out=src/omnia_langchain_runtime \
    proto/runtime.proto

# Run tests
pytest

# Lint and format
ruff check src tests
ruff format src tests

# Type checking
mypy src
```

## License

Apache License 2.0
