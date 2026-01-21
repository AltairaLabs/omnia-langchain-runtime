---
title: Configuration
description: How to configure the Omnia LangChain Runtime
sidebar:
  order: 2
---

The runtime is configured via environment variables.

## Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OMNIA_AGENT_NAME` | Name of the agent | `my-agent` |
| `OMNIA_NAMESPACE` | Kubernetes namespace | `default` |

## PromptPack Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `OMNIA_PROMPTPACK_PATH` | Path to the PromptPack file | `/etc/omnia/pack/pack.json` |
| `OMNIA_PROMPT_NAME` | Name of the prompt to use | `default` |

## Provider Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `OMNIA_PROVIDER_TYPE` | Provider type | `claude`, `openai`, `gemini`, `ollama`, `mock` |
| `OMNIA_PROVIDER_MODEL` | Model identifier | `claude-sonnet-4-20250514` |

## Session Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OMNIA_SESSION_TYPE` | Session storage type | `memory` |
| `OMNIA_SESSION_URL` | Redis URL (if using redis) | `redis://localhost:6379` |

## Tools Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `OMNIA_TOOLS_CONFIG` | Path to tools configuration | `/etc/omnia/tools/tools.yaml` |

## Server Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OMNIA_GRPC_PORT` | gRPC server port | `9000` |
| `OMNIA_HEALTH_PORT` | Health check port | `9001` |

## Example Configuration

```bash
# Required
export OMNIA_AGENT_NAME=my-agent
export OMNIA_NAMESPACE=default

# PromptPack
export OMNIA_PROMPTPACK_PATH=/etc/omnia/pack/pack.json
export OMNIA_PROMPT_NAME=default

# Provider
export OMNIA_PROVIDER_TYPE=claude
export OMNIA_PROVIDER_MODEL=claude-sonnet-4-20250514

# Session (optional)
export OMNIA_SESSION_TYPE=memory

# Server ports
export OMNIA_GRPC_PORT=9000
export OMNIA_HEALTH_PORT=9001
```
