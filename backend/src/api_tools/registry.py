"""Tool registry for discovering and managing available API tools."""

from __future__ import annotations

from typing import Any

from api_tools.base import BaseTool


class ToolRegistry:
    """Central registry that maps tool codes to tool instances."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.tool_code] = tool

    def get(self, tool_code: str) -> BaseTool | None:
        return self._tools.get(tool_code)

    def list_tools(self) -> list[dict[str, Any]]:
        return [tool.to_schema() for tool in self._tools.values()]

    @property
    def tool_codes(self) -> list[str]:
        return list(self._tools.keys())


_global_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    """Return the global tool registry, creating and populating it on first call."""
    global _global_registry  # noqa: PLW0603
    if _global_registry is None:
        _global_registry = ToolRegistry()
        _register_builtin_tools(_global_registry)
    return _global_registry


def _register_builtin_tools(registry: ToolRegistry) -> None:
    from api_tools.account_api import AccountQueryAPITool
    from api_tools.bill_payment_api import BillPaymentAPITool
    from api_tools.fund_api import FundQueryAPITool
    from api_tools.transfer_api import TransferAPITool

    registry.register(TransferAPITool())
    registry.register(BillPaymentAPITool())
    registry.register(FundQueryAPITool())
    registry.register(AccountQueryAPITool())
