# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY proto/ ./proto/

# Install the package
# First install promptpack dependencies from GitHub (not yet on PyPI)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        "git+https://github.com/AltairaLabs/promptpack-python.git#subdirectory=packages/promptpack" \
        "git+https://github.com/AltairaLabs/promptpack-python.git#subdirectory=packages/promptpack-langchain" && \
    pip install --no-cache-dir .

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source for reference
COPY src/ ./src/
COPY proto/ ./proto/

# Create non-root user
RUN useradd --create-home --shell /bin/bash omnia
USER omnia

# Expose ports
EXPOSE 9000 9001

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import grpc; ch = grpc.insecure_channel('localhost:9000'); grpc.channel_ready_future(ch).result(timeout=5)" || exit 1

# Default environment variables
ENV OMNIA_GRPC_PORT=9000 \
    OMNIA_HEALTH_PORT=9001 \
    OMNIA_SESSION_TYPE=memory \
    OMNIA_PROMPTPACK_PATH=/etc/omnia/pack/pack.json \
    OMNIA_PROMPT_NAME=default

# Run the server
ENTRYPOINT ["python", "-m", "omnia_langchain_runtime"]
