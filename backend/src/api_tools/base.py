"""Base API tool abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolParameter:
    name: str
    description: str
    param_type: str = "string"
    required: bool = True


class BaseTool(ABC):
    """Abstract base class for API tools used by skills."""

    @property
    @abstractmethod
    def tool_code(self) -> str:
        """Unique identifier for this tool."""

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Human-readable name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this tool does."""

    @property
    @abstractmethod
    def parameters(self) -> list[ToolParameter]:
        """Parameter definitions."""

    @abstractmethod
    async def call(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute the API call and return results."""

    def validate_params(self, params: dict[str, Any]) -> list[str]:
        """Return list of missing required parameter names."""
        required = {p.name for p in self.parameters if p.required}
        return sorted(name for name in required if not params.get(name))

    def to_schema(self) -> dict[str, Any]:
        """Return a JSON-serializable schema for this tool."""
        return {
            "tool_code": self.tool_code,
            "tool_name": self.tool_name,
            "description": self.description,
            "parameters": [
                {
                    "name": p.name,
                    "description": p.description,
                    "type": p.param_type,
                    "required": p.required,
                }
                for p in self.parameters
            ],
        }
