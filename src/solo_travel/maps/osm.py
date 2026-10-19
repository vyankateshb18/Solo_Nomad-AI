"""Map rendering module using PyDeck and OpenStreetMap tiles."""
from typing import Dict, Any, Optional
import pydeck as pdk
from solo_travel.providers.weather import WeatherProvider

_weather_provider = WeatherProvider()


def get_city_coordinates(city_name: str) -> Optional[Dict[str, float]]:
    """Geocode city to lat/lon using Open-Meteo geocoding."""
    w = _weather_provider.search(city_name)
    # Re-use Open-Meteo geocoding
    try:
        import httpx
        with httpx.Client(timeout=5) as client:
            resp = client.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city_name, "count": 1})
            if resp.status_code == 200:
                results = resp.json().get("results")
                if results:
                    return {"lat": results[0]["latitude"], "lon": results[0]["longitude"]}
    except Exception:
        pass

    # Basic coordinate fallbacks for major Indian destinations
    fallbacks = {
        "delhi": {"lat": 28.6139, "lon": 77.2090},
        "new delhi": {"lat": 28.6139, "lon": 77.2090},
        "varanasi": {"lat": 25.3176, "lon": 82.9739},
        "mumbai": {"lat": 19.0760, "lon": 72.8777},
        "bengaluru": {"lat": 12.9716, "lon": 77.5946},
        "rishikesh": {"lat": 30.0869, "lon": 78.2676},
        "goa": {"lat": 15.2993, "lon": 74.1240},
        "jaipur": {"lat": 26.9124, "lon": 75.7873},
        "hampi": {"lat": 15.3350, "lon": 76.4600},
        "gokarna": {"lat": 14.5479, "lon": 74.3188},
    }
    return fallbacks.get(city_name.strip().lower())


def create_route_map(origin: str, destination: str, weather_info: Optional[Dict[str, Any]] = None) -> Optional[pdk.Deck]:
    """
    Renders an interactive OpenStreetMap view connecting Origin and Destination
    with markers for transit and weather alerts.
    """
    orig_coords = get_city_coordinates(origin)
    dest_coords = get_city_coordinates(destination)

    if not orig_coords or not dest_coords:
        return None

    # Points data
    points_data = [
        {
            "name": f"Origin: {origin}",
            "coordinates": [orig_coords["lon"], orig_coords["lat"]],
            "color": [59, 130, 246, 220],  # Blue
            "radius": 15000,
            "type": "Origin Hub"
        },
        {
            "name": f"Destination: {destination}",
            "coordinates": [dest_coords["lon"], dest_coords["lat"]],
            "color": [239, 68, 68, 220],  # Red
            "radius": 20000,
            "type": "Destination & Stays"
        }
    ]

    # Transit route line
    line_data = [
        {
            "from_name": origin,
            "to_name": destination,
            "from": [orig_coords["lon"], orig_coords["lat"]],
            "to": [dest_coords["lon"], dest_coords["lat"]],
        }
    ]

    # Scatter plot layer for destination & origin markers
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=points_data,
        get_position="coordinates",
        get_color="color",
        get_radius="radius",
        pickable=True,
    )

    # Line layer for transit corridor
    line_layer = pdk.Layer(
        "LineLayer",
        data=line_data,
        get_source_position="from",
        get_target_position="to",
        get_color=[99, 102, 241, 180],  # Purple glow line
        get_width=5,
        pickable=True,
    )

    # Midpoint for initial camera center
    mid_lat = (orig_coords["lat"] + dest_coords["lat"]) / 2
    mid_lon = (orig_coords["lon"] + dest_coords["lon"]) / 2

    view_state = pdk.ViewState(
        latitude=mid_lat,
        longitude=mid_lon,
        zoom=5.5,
        pitch=20,
    )

    # Use OpenStreetMap raster map style
    return pdk.Deck(
        layers=[line_layer, scatter_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={"text": "{name}\n{type}"}
    )
