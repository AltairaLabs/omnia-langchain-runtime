# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""Entry point for the Omnia LangChain Runtime."""

import asyncio
import logging
import sys

from omnia_langchain_runtime.config import load_config
from omnia_langchain_runtime.handler import LangChainHandler
from omnia_langchain_runtime.server import serve


def main() -> int:
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    try:
        config = load_config()
        logger.info(
            "Starting Omnia LangChain Runtime",
            extra={
                "agent_name": config.agent_name,
                "namespace": config.namespace,
                "provider": config.provider_type,
            },
        )

        handler = LangChainHandler(config)
        asyncio.run(serve(handler, config))
        return 0

    except Exception as e:
        logger.exception("Failed to start runtime: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
