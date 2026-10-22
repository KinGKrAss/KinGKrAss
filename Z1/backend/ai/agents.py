from .tools import ToolDefinition, ToolRegistry


class AgentCoordinator:
    def __init__(self) -> None:
        self.tools = ToolRegistry()
        self.tools.register(ToolDefinition(name="reporting", description="Erstellt Modulberichte"))
        self.tools.register(ToolDefinition(name="task-router", description="Leitet Aufgaben an Module"))

    def status(self) -> dict:
        return {
            "coordinator": "zoe",
            "active": True,
            "tool_count": len(self.tools.list_tools()),
        }
