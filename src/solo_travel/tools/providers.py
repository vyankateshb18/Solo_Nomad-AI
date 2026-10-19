"""Expose provider functions as typed CrewAI tools."""
from crewai.tools import tool
from solo_travel.providers.transport import TransportProvider
from solo_travel.providers.weather import WeatherProvider

_transport_provider = TransportProvider()
_weather_provider = WeatherProvider()


@tool("Search Trains")
def search_trains_tool(origin: str, destination: str) -> str:
    """
    Search verified train schedules, train numbers, timings, and indicative sleeper/chair car fares in INR.
    """
    options = _transport_provider.search_trains(origin, destination)
    if not options:
        return f"No train routes found between {origin} and {destination}."

    lines = []
    for opt in options:
        status_tag = "[Indicative Tariff]" if opt.indicative_only else "[Verified Schedule]"
        lines.append(
            f"• {opt.identifier} ({opt.provider_or_operator}) {status_tag}:\n"
            f"  Route: {opt.departure_station} ({opt.departure_time}) ➔ {opt.arrival_station} ({opt.arrival_time})\n"
            f"  Duration: ~{opt.duration_hours} hrs | Fare: ₹{opt.fare_inr:,.0f} | Source: {opt.source_attribution}"
        )
    return "\n\n".join(lines)


@tool("Search Buses")
def search_buses_tool(origin: str, destination: str) -> str:
    """
    Search state road transport buses (e.g. UPSRTC, UTC, KSRTC) and long-distance sleeper buses.
    """
    options = _transport_provider.search_buses(origin, destination)
    if not options:
        return f"No bus routes found between {origin} and {destination}."

    lines = []
    for opt in options:
        status_tag = "[Indicative Tariff]" if opt.indicative_only else "[Verified Service]"
        lines.append(
            f"• {opt.identifier} ({opt.provider_or_operator}) {status_tag}:\n"
            f"  Terminal: {opt.departure_station} ({opt.departure_time}) ➔ {opt.arrival_station} ({opt.arrival_time})\n"
            f"  Duration: ~{opt.duration_hours} hrs | Fare: ₹{opt.fare_inr:,.0f} | Source: {opt.source_attribution}"
        )
    return "\n\n".join(lines)


@tool("Get Weather")
def get_weather_tool(destination: str) -> str:
    """
    Fetch current live weather conditions, temperature, and rain probability using Open-Meteo.
    """
    w = _weather_provider.search(destination)
    if w.get("status") != "success":
        return f"Weather data unavailable for {destination}: {w.get('note', 'lookup error')}"

    return (
        f"Weather for {destination} (via {w['source']}):\n"
        f"• Current Temp: {w['current_temp_c']}°C (Wind: {w['wind_speed_kmh']} km/h)\n"
        f"• Daily Range: {w['temp_min_c']}°C - {w['temp_max_c']}°C\n"
        f"• Rain Probability: {w['rain_prob_percent']}%"
    )
