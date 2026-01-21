---
title: Quickstart
description: Get up and running with the Omnia LangChain Runtime
sidebar:
  order: 3
---

This guide will help you get the Omnia LangChain Runtime running locally.

## Running the Server

### Using the CLI

```bash
omnia-langchain-runtime
```

### Using Python Module

```bash
python -m omnia_langchain_runtime
```

## Docker

Build and run using Docker:

```bash
# Build the image
docker build -t omnia-langchain-runtime .

# Run with mock provider
docker run -e OMNIA_AGENT_NAME=test \
           -e OMNIA_NAMESPACE=default \
           -e OMNIA_PROVIDER_TYPE=mock \
           -p 9000:9000 \
           omnia-langchain-runtime
```

## Kubernetes

Deploy using the Omnia AgentRuntime CRD with `framework: langchain`:

```yaml
apiVersion: omnia.altairalabs.ai/v1
kind: AgentRuntime
metadata:
  name: my-langchain-agent
spec:
  framework: langchain
  provider:
    type: claude
    model: claude-sonnet-4-20250514
```

## Next Steps

- Configure [providers](/providers/) for your LLM backend
- Set up [session management](/session/) for conversation persistence
- Add [tools](/tools/) to extend agent capabilities
