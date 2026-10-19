"""Official Model Context Protocol (MCP) Server for Solo Travel Intelligence Platform."""
import asyncio
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from solo_travel.providers.transport import TransportProvider
from solo_travel.providers.weather import WeatherProvider

server = Server("solo-travel-mcp-server")
_transport_provider = TransportProvider()
_weather_provider = WeatherProvider()


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Expose typed travel intelligence tools via MCP protocol."""
    return [
        Tool(
            name="search_trains",
            description="Search verified Indian railway trains (IRCTC/RailRadar) between origin and destination stations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin city or station name"},
                    "destination": {"type": "string", "description": "Destination city or station name"},
                },
                "required": ["origin", "destination"],
            },
        ),
        Tool(
            name="search_buses",
            description="Search state transport buses (UPSRTC, UTC, KSRTC) and long-distance sleeper buses.",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin city or bus terminal"},
                    "destination": {"type": "string", "description": "Destination city or bus terminal"},
                },
                "required": ["origin", "destination"],
            },
        ),
        Tool(
            name="get_weather",
            description="Fetch current live weather conditions, daily temperatures, and rain probability using Open-Meteo.",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "Destination city name"},
                },
                "required": ["destination"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle incoming tool invocation requests from MCP clients."""
    args = arguments or {}

    if name == "search_trains":
        origin = args.get("origin", "")
        destination = args.get("destination", "")
        opts = _transport_provider.search_trains(origin, destination)
        if not opts:
            return [TextContent(type="text", text=f"No trains found between {origin} and {destination}.")]

        lines = [f"• {opt.identifier} ({opt.provider_or_operator}) | {opt.departure_station} ➔ {opt.arrival_station} | Fare: ₹{opt.fare_inr:,.0f}" for opt in opts]
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "search_buses":
        origin = args.get("origin", "")
        destination = args.get("destination", "")
        opts = _transport_provider.search_buses(origin, destination)
        if not opts:
            return [TextContent(type="text", text=f"No buses found between {origin} and {destination}.")]

        lines = [f"• {opt.identifier} ({opt.provider_or_operator}) | Terminal: {opt.departure_station} | Fare: ₹{opt.fare_inr:,.0f}" for opt in opts]
        return [TextContent(type="text", text="\n".join(lines))]

    elif name == "get_weather":
        destination = args.get("destination", "")
        w = _weather_provider.search(destination)
        if w.get("status") != "success":
            return [TextContent(type="text", text=f"Weather lookup error: {w.get('note', 'unavailable')}")]

        summary = f"Weather for {destination}:\n• Current: {w['current_temp_c']}°C\n• Rain Chance: {w['rain_prob_percent']}%\n• Source: {w['source']}"
        return [TextContent(type="text", text=summary)]

    else:
        raise ValueError(f"Unknown MCP tool: {name}")


async def main():
    """Run the MCP server over standard IO transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
