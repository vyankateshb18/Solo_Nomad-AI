"""MCP Client helper allowing CrewAI agents and services to discover and invoke tools over MCP."""
from typing import List, Dict, Any
from mcp.server import Server
from solo_travel.mcp.server import handle_list_tools, handle_call_tool


class LocalMCPClient:
    """
    Direct in-process and protocol-level client for the Solo Travel MCP server.
    Ensures seamless execution and verified schema compliance without spawning external shell processes in unit tests.
    """
    async def list_tools(self) -> List[Dict[str, Any]]:
        """Discover tools exposed by the MCP server."""
        tools = await handle_list_tools()
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.inputSchema
            }
            for t in tools
        ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Invoke a tool on the MCP server and return text content."""
        results = await handle_call_tool(tool_name, arguments)
        return "\n".join(r.text for r in results if hasattr(r, "text"))
