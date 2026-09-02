
import asyncio
import http_client
from datetime import datetime, timezone
from asyncddgs import aDDGS

# ---------------------------------------------------------------------------- #
#                             Boilerplate / Helper                             #
# ---------------------------------------------------------------------------- #
WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

# ------------------------------- normalization ------------------------------ #
def format_measurement(field: str, data: dict, units: dict) -> str:
    """extracts value and unit from dict and concats them"""
    val = data.get(field)
    unit = units.get(field, "")
    
    if val is None:
        return "N/A"
        
    return f"{val} {unit}".strip()

def normalize_current(u, c):
    code = c.pop("weather_code")
    c["weather_description"] = WMO_WEATHER_CODES[code]
    
    FIELD_MAP = {
        "time": "time",
        "weather_description": "weather_description",
        "temperature": "temperature_2m",
        "apparent_temperature": "apparent_temperature",
        "humidity": "relative_humidity_2m",
        "wind_speed": "wind_speed_10m",
        "precipitation": "precipitation",
    }
    
    normalized = {
        target_key: format_measurement(src_key,c,u)
        for target_key, src_key in FIELD_MAP.items()
    }
    
    # return payload if everything is fine
    return normalized

def normalize_daily(units, daily):
    # normalize parallel arrays
    FIELD_MAP = {
        "time": "time",
        "weather_description": "weather_description",
        "max_temperature": "temperature_2m_max",
        "min_temperature": "temperature_2m_min",
        "precipitation_sum": "precipitation_sum",
        "max_wind_speed": "wind_speed_10m_max",
    }

    # Transpose parallel lists into individual day dictionaries
    keys = list(daily.keys())
    day_records = [dict(zip(keys, values)) for values in zip(*daily.values())]

    normalized_forecast = []
    for day in day_records:
        # Convert WMO code to description
        code = day.get("weather_code")
        day["weather_description"] = WMO_WEATHER_CODES.get(code, "Unknown")

        # Map and format each field for the target dictionary
        normalized_day = {
            target_key: format_measurement(src_key, day, units)
            for target_key, src_key in FIELD_MAP.items()
        }
        normalized_forecast.append(normalized_day)


    # return payload if everything is fine
    return normalized_forecast

def normalize_search(raw_results: list[dict]) -> list[dict]:
    """Normalizes raw search result keys to standard fields ('title', 'url', 'snippet')."""
    FIELD_MAP = {
        "title": "title",
        "url": "href",
        "snippet": "body",
    }

    return [
        {target_key: item.get(src_key, "") for target_key, src_key in FIELD_MAP.items()}
        for item in raw_results
    ]

# ---------------------------------------------------------------------------- #
#                                  Exceptions                                  #
# ---------------------------------------------------------------------------- #
class LocationNotFoundError(Exception):
    """Raised when a city search returns no results."""
    pass
class ForecastNotFoundError(Exception):
    """Raised when a weather forecast query returns no forecast."""
    pass
class SearchNotFoundError(Exception):
    """Raised when a web search returns no results."""
    pass
# ---------------------------------------------------------------------------- #
#                                    Utility                                   #
# ---------------------------------------------------------------------------- #
# ----------------------------------- Local ---------------------------------- #
async def get_current_time() -> str:
    """Gets UTC standardized computer time."""
    now_utc = datetime.now(timezone.utc)
    return now_utc.strftime("%A, %b %d, %Y at %I:%M %p UTC")

# ------------------------------------ Api ----------------------------------- #
# Open Meteo #
async def get_geocode(place: str, count: int = 1) -> dict:
    """Searches for geographic information given a location name."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": place,
        "count": count,
    }
    # fetch
    raw_response = await http_client.fetch_json(url, params)
    results = raw_response.get("results")
    
    # raise error
    if not results:
        raise LocationNotFoundError(f"No coordinates for '{place}'")
    
    # extract domain payload
    geo_data = results[0]
    
    # return payload if everything is fine
    return geo_data  

async def get_current_weather(
    latitude: float, 
    longitude: float, 
    temp_unit: str = "celsius", 
    wind_unit: str = "kmh"
) -> dict:
    """Searches for CURRENT weather forecast at given coordinates."""
    url = "https://api.open-meteo.com/v1/forecast"

    # ADD: standardize temp and wind units to remove possibility of ai hallucination
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_unit": temp_unit,
        "wind_speed_unit": wind_unit,
        "current": "weather_code,temperature_2m,apparent_temperature,precipitation,relative_humidity_2m,wind_speed_10m",
    }
    # fetches raw forecast response from api
    raw_response = await http_client.fetch_json(url, params)
    
    #extract domain payload and units
    u = raw_response.get("current_units")
    c = raw_response.get("current")
    
    # raise error
    if not c:
        raise ForecastNotFoundError(f"No forecast for 'latitude: {latitude}, longitude: {longitude}'")
    
    # normalize data
    normalized = normalize_current(u, c)
    
    # return payload if everything is fine
    return normalized
    
async def get_daily_weather(
    latitude: float, 
    longitude: float, 
    start_date: str = datetime.now().strftime("%Y-%m-%d"),
    end_date: str = datetime.now().strftime("%Y-%m-%d"),
    temp_unit: str = "celsius", 
    wind_unit: str = "kmh"
) -> dict:
    """Fetches a multi-day forecast for given coordinates and date range (YYYY-MM-DD)."""
    url = "https://api.open-meteo.com/v1/forecast"

    # ADD: standardize temp and wind units to remove possibility of ai hallucination
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_unit": temp_unit,
        "wind_speed_unit": wind_unit,
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "auto", # midnight cutoffs
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
    }
    # fetches raw forecast response from api, parallel arrays
    raw_response = await http_client.fetch_json(url, params)
    
    #extract domain payload and units
    units = raw_response.get("daily_units")
    daily = raw_response.get("daily")
    
    # raise error
    if not daily:
        raise ForecastNotFoundError(f"No forecast for 'latitude: {latitude}, longitude: {longitude}'")
    
    # normalized raw response
    normalized = normalize_daily(units, daily)
    
    # return payload if everything is fine
    return normalized
    
# DuckDuckGo #
async def perform_web_search(query: str, max_results: int = 3) -> list[dict]:
    """Asynchronously searches the web using DuckDuckGo and returns normalized snippets."""
    try:
        # Initialize the async client and fetch results
        async with aDDGS() as ddgs:
            # .text() is the standard text search method in DDGS
            raw_results = await ddgs.text(query, max_results=max_results)
    except Exception as e:
        # Catch rate limits or network issues from the DDG library
        raise Exception(f"Search provider error: {str(e)}")

    # Raise our custom error if the list is empty or None
    if not raw_results:
        raise SearchNotFoundError(f"No results found for '{query}'")
    
    # normalize
    normalized = normalize_search(raw_results)
    
    # Return payload if everything is fine
    return normalized

# # ---------------------------------------------------------------------------- #
# #                                     debug                                    #
# # ---------------------------------------------------------------------------- #
# async def mainfr():
#     # geo_data = await get_geocode(place="taipei")
    
#     # forecast = await get_daily_weather(latitude=geo_data["latitude"], longitude=geo_data["longitude"], start_date="2026-08-25", end_date="2026-08-29")
#     # # Properly close connections before exiting
#     # print(forecast)
    
#     r = await perform_web_search("stock price of nvidia right now")
#     print(r)
#     await http_client.close_shared_session()

# asyncio.run(mainfr())