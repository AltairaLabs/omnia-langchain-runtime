---
title: Deployment
description: Deploying the Omnia LangChain Runtime
sidebar:
  order: 0
---

This guide covers deployment options for the Omnia LangChain Runtime.

## Docker

### Building the Image

```bash
docker build -t omnia-langchain-runtime .
```

### Running

```bash
docker run -d \
  -e OMNIA_AGENT_NAME=my-agent \
  -e OMNIA_NAMESPACE=default \
  -e OMNIA_PROVIDER_TYPE=claude \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -p 9000:9000 \
  -p 9001:9001 \
  omnia-langchain-runtime
```

## Kubernetes

### AgentRuntime CRD

Deploy using the Omnia AgentRuntime Custom Resource:

```yaml
apiVersion: omnia.altairalabs.ai/v1
kind: AgentRuntime
metadata:
  name: my-langchain-agent
  namespace: default
spec:
  framework: langchain
  replicas: 2
  provider:
    type: claude
    model: claude-sonnet-4-20250514
    secretRef:
      name: anthropic-credentials
  session:
    type: redis
    url: redis://redis:6379
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

### Secrets

Create secrets for API keys:

```bash
kubectl create secret generic anthropic-credentials \
  --from-literal=ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
```

## Health Checks

Configure Kubernetes probes:

```yaml
livenessProbe:
  grpc:
    port: 9001
  initialDelaySeconds: 10
  periodSeconds: 10
readinessProbe:
  grpc:
    port: 9001
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Scaling

The runtime is stateless (when using Redis sessions) and can be horizontally scaled:

```bash
kubectl scale deployment my-langchain-agent --replicas=5
```
