---
title: Installation
description: How to install the Omnia LangChain Runtime
sidebar:
  order: 1
---

## Prerequisites

- Python 3.10 or higher
- pip package manager

## Installation

Install the runtime using pip:

```bash
pip install omnia-langchain-runtime
```

### With Redis Support

If you need Redis session storage:

```bash
pip install omnia-langchain-runtime[redis]
```

## Development Installation

For development, clone the repository and install in editable mode:

```bash
git clone https://github.com/AltairaLabs/omnia-langchain-runtime.git
cd omnia-langchain-runtime
pip install -e ".[dev]"
```

## Verify Installation

Verify the installation by checking the version:

```bash
python -c "import omnia_langchain_runtime; print('Installation successful')"
```
