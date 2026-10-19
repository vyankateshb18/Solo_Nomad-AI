"""Live Weather provider using Open-Meteo public API (no API key required)."""
from typing import Dict, Any, Optional
import httpx
from solo_travel.providers.base import BaseTravelProvider


class WeatherProvider(BaseTravelProvider):
    """Fetches real-time weather and forecast via Open-Meteo."""
    GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, timeout_seconds: int = 5, cache_ttl_seconds: int = 7200):
        super().__init__(cache_ttl_seconds=cache_ttl_seconds)
        self.timeout = timeout_seconds

    def search(self, destination: str, **kwargs) -> Dict[str, Any]:
        """Fetch current temperature, weather conditions, and forecast."""
        cache_key = f"weather_{destination.strip().lower()}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        try:
            # 1. Geocode destination to latitude/longitude
            with httpx.Client(timeout=self.timeout) as client:
                geo_resp = client.get(self.GEO_URL, params={"name": destination, "count": 1})
                if geo_resp.status_code != 200:
                    return {"status": "unavailable", "note": "Geocoding service error"}

                geo_data = geo_resp.json()
                results = geo_data.get("results")
                if not results:
                    return {"status": "unavailable", "note": f"Could not locate destination: '{destination}'"}

                lat = results[0]["latitude"]
                lon = results[0]["longitude"]

                # 2. Fetch current weather and 3-day forecast
                weather_resp = client.get(
                    self.WEATHER_URL,
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current_weather": "true",
                        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                        "timezone": "auto"
                    }
                )

                if weather_resp.status_code != 200:
                    return {"status": "unavailable", "note": "Weather forecast service error"}

                w_data = weather_resp.json()
                current = w_data.get("current_weather", {})
                daily = w_data.get("daily", {})

                summary = {
                    "status": "success",
                    "destination": destination,
                    "current_temp_c": current.get("temperature"),
                    "wind_speed_kmh": current.get("windspeed"),
                    "temp_max_c": daily.get("temperature_2m_max", [None])[0],
                    "temp_min_c": daily.get("temperature_2m_min", [None])[0],
                    "rain_prob_percent": daily.get("precipitation_probability_max", [0])[0],
                    "source": "Open-Meteo (Live Public Feed)"
                }

                self.cache.set(cache_key, summary)
                return summary

        except Exception as exc:
            return {"status": "unavailable", "note": f"Weather lookup failed: {str(exc)}"}
