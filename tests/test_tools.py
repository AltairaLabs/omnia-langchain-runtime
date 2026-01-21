# Copyright 2025 Altaira Labs
# SPDX-License-Identifier: Apache-2.0

"""Tests for tool adapters."""

from pathlib import Path

import pytest

from omnia_langchain_runtime.tools.config import (
    HandlerConfig,
    ToolDefinition,
    ToolsConfig,
    load_tools_config,
)


class TestToolsConfig:
    """Tests for tools configuration parsing."""

    def test_parse_empty_config(self, tmp_path: Path) -> None:
        """Test parsing empty config."""
        config_file = tmp_path / "tools.yaml"
        config_file.write_text("{}")

        config = load_tools_config(config_file)
        assert config.handlers == []

    def test_parse_http_handler(self, tmp_path: Path) -> None:
        """Test parsing HTTP handler."""
        config_file = tmp_path / "tools.yaml"
        config_file.write_text("""
handlers:
  - name: weather
    type: http
    endpoint: http://api.weather.com/v1
    tool:
      name: get_weather
      description: Get weather for a location
      inputSchema:
        type: object
        properties:
          location:
            type: string
        required:
          - location
    httpConfig:
      method: POST
      headers:
        X-API-Key: test-key
      contentType: application/json
    timeout: 30s
    retries: 2
""")

        config = load_tools_config(config_file)

        assert len(config.handlers) == 1
        handler = config.handlers[0]

        assert handler.name == "weather"
        assert handler.type == "http"
        assert handler.endpoint == "http://api.weather.com/v1"
        assert handler.timeout == "30s"
        assert handler.retries == 2

        assert handler.tool is not None
        assert handler.tool.name == "get_weather"
        assert "location" in handler.tool.input_schema["properties"]

        assert handler.http_config is not None
        assert handler.http_config.method == "POST"
        assert handler.http_config.headers == {"X-API-Key": "test-key"}

    def test_get_handler(self) -> None:
        """Test getting handler by name."""
        config = ToolsConfig(
            handlers=[
                HandlerConfig(name="handler1", type="http", endpoint="http://test1"),
                HandlerConfig(name="handler2", type="http", endpoint="http://test2"),
            ]
        )

        handler = config.get_handler("handler1")
        assert handler is not None
        assert handler.endpoint == "http://test1"

        assert config.get_handler("nonexistent") is None

    def test_get_tool_handler(self) -> None:
        """Test getting handler by tool name."""
        config = ToolsConfig(
            handlers=[
                HandlerConfig(
                    name="handler1",
                    type="http",
                    endpoint="http://test",
                    tool=ToolDefinition(
                        name="my_tool",
                        description="Test tool",
                        input_schema={},
                    ),
                ),
            ]
        )

        handler = config.get_tool_handler("my_tool")
        assert handler is not None
        assert handler.name == "handler1"

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test error when file not found."""
        with pytest.raises(FileNotFoundError):
            load_tools_config(tmp_path / "nonexistent.yaml")
