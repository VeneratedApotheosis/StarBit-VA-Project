
import asyncio
import http_client
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# ---------------------------------------------------------------------------- #
#                                  Exceptions                                  #
# ---------------------------------------------------------------------------- #
class LocationNotFoundError(Exception):
    """Raised when a city search returns no results."""
    pass

# ---------------------------------------------------------------------------- #
#                                    Utility                                   #
# ---------------------------------------------------------------------------- #
# ----------------------------------- Local ---------------------------------- #
async def get_current_time() -> str:
    """Gets local computer time in a voice-friendly format."""
    now_utc = datetime.now(timezone.utc)
    return now_utc.strftime("%A, %b %d, %Y at %I:%M %p UTC")

# ------------------------------------ Api ----------------------------------- #
async def get_geocode(place: str, count: int = 1) -> dict:
    """Searches for geographic information given a location name."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": place,
        "count": count,
    }
    # fetch
    data = await http_client.fetch_json(url, params)
    results = data.get("results")
    
    # raise error
    if not results:
        raise LocationNotFoundError(f"No coordinates for '{place}'")
    
    # return data if everything is fine
    return results

async def get_weather_coords(latitude: float, longitude: float, unit: str = "celsius") -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    temp_unit = "fahrenheit" if unit.lower().startswith("f") else "celsius"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_unit": temp_unit,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m",
    }
    return await http_client.fetch_json(url, params)
    
# # ---------------------------------------------------------------------------- #
# #                                     debug                                    #
# # ---------------------------------------------------------------------------- #
# async def mainfr():
#     try:
#         local = await get_geocode("paris")
#         print(local)
#     finally:
#         # Properly close connections before exiting
#         await http_client.close_shared_session()

# asyncio.run(mainfr())