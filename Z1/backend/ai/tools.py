from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ToolDefinition:
    name: str
    description: str


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool

    def list_tools(self) -> list[dict[str, Any]]:
        return [{"name": tool.name, "description": tool.description} for tool in self._tools.values()]
