import asyncio
import functools

import aiohttp
from pipecat.adapters.schemas.direct_function import tool_options
from pipecat.services.llm_service import FunctionCallParams

import utility

REGISTERED_TOOLS = []
# ---------------------------------------------------------------------------- #
#                          Boilerplate / Helper Funcs                          #
# ---------------------------------------------------------------------------- #
def register_tool(func):
    REGISTERED_TOOLS.append(func)
    return func

def safe_tool(func):
    """Decorator to automatically catch exceptions and send them to the LLM."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Run the actual tool function
            return await func(*args, **kwargs)
        
        # exception wrapper
        except Exception as e:
            match e:
                case utility.UtilityError():
                    error_msg = str(e)
                case asyncio.TimeoutError():
                    error_msg = "The service timed out while responding."
                case aiohttp.ClientError():
                    error_msg = "The external service is currently unreachable."
                case _:
                    error_msg = f"An unexpected error occurred: {e!s}"
            
            if args and isinstance(args[0], FunctionCallParams):
                params = args[0]
                await params.result_callback({"error": error_msg})
            else:
                raise e
                
    return wrapper

def pick_keys(source: dict, keys: set | list) -> dict:
    """Extracts only the specified keys from a source dictionary."""
    return {k: source[k] for k in keys if k in source}

# ---------------------------------------------------------------------------- #
#                                     Tools                                    #
# ---------------------------------------------------------------------------- #
@register_tool
@tool_options(cancel_on_interruption=True, timeout_secs=30)
@safe_tool
async def get_time_tool(params: FunctionCallParams):
    """Gets the current time from computer"""
    current_time = await utility.get_current_time()
    formatted = {"current_time": current_time}
    await params.result_callback(formatted)
    
@register_tool
@tool_options(cancel_on_interruption=True, timeout_secs=30)
@safe_tool
async def get_geocode_tool(params: FunctionCallParams, place: str, language: str):
    """Searches for geographic coordinates (latitude and longitude) given a location name (and optionally language of the place string). 
    
    Args:
        place: The name of the city, region, or landmark to geocode (e.g., 'Paris, France' or 'Tokyo').
        language: Two-letter ISO language code that argument or parameter "place" was written in  (e.g., 'en', 'zh').
    """
    geo_data = await utility.get_geocode(place=place, language=language)
    
    # pruning
    allowed_keys = {'name', 'longitude', 'latitude'}
    pruned_data = pick_keys(geo_data,allowed_keys)
    
    await params.result_callback(pruned_data)
    
@register_tool
@tool_options(cancel_on_interruption=True, timeout_secs=30)
@safe_tool
async def get_current_forecast_tool(params: FunctionCallParams, place: str, language: str):
    """Provides the CURRENT weather forecast at given place (and optionally language of the place string). 
    
    Returns current weather forecast including 'weather_description', 'temperature', 'apparent_temperature', 'relative_humidity', 'wind_speed', 'cloud_cover', and 'precipitation'.
    
    Args:
        place: The name of the city, region, or landmark (e.g., 'Paris, France' or 'Tokyo').
        language: Two-letter ISO language code that argument or parameter "place" was written in (e.g., 'en', 'zh').
    """
    
    # fetch relevant geographic data
    geo_data = await utility.get_geocode(place=place, language=language)

    # fetch forecast
    latitude = geo_data["latitude"]
    longitude = geo_data["longitude"]
    forecast_data = await utility.get_current_weather(latitude,longitude)
    
    await params.result_callback(forecast_data)

@register_tool
@tool_options(cancel_on_interruption=True, timeout_secs=30)
@safe_tool
async def get_daily_forecast_tool(params: FunctionCallParams, place: str, language: str, start_date: str, end_date: str):
    """Provides daily weather forecasts over a range of dates for a specified location (and optionally language of the place string).

    Returns daily metrics including weather description, maximum temperature, 
    minimum temperature, total precipitation, and maximum wind speed for each day 
    between the start and end dates.

    Args:
        place: The name of the city, region, or landmark (e.g., 'Paris, France' or 'Tokyo').
        language: Two-letter ISO language code that argument or parameter "place" was written in (e.g., 'en', 'zh').
        start_date: The start date of the forecast range in 'YYYY-MM-DD' format.
        end_date: The end date of the forecast range in 'YYYY-MM-DD' format.
    """
    
    # fetch relevant geographic data
    geo_data = await utility.get_geocode(place=place, language=language)

    # fetch forecast
    latitude = geo_data["latitude"]
    longitude = geo_data["longitude"]
    forecast_data = await utility.get_daily_weather(
        latitude,
        longitude,
        start_date=start_date,
        end_date=end_date
    )
    
    await params.result_callback(forecast_data)
    
@register_tool
@tool_options(cancel_on_interruption=True, timeout_secs=15)
@safe_tool
async def web_search_tool(params: FunctionCallParams, query: str):
    """Searches the web for real-time information, current facts, news, or specific topics. This is however limited by the inability to access webpages, so if dynamic elements need to be rendered in order to received the correct information (eg. stock prices) you will be unable to find those information.

    Use this tool when answering questions about events, facts, or data that require up-to-date web access.

    Args:
        query: Concise, keyword-driven search terms (e.g., 'FIFA World Cup 2026 winner'.
    """
    # search utility
    search_results = await utility.perform_web_search(query=query)

    await params.result_callback(search_results)
    
@register_tool
@tool_options(cancel_on_interruption=True, timeout_secs=15)
@safe_tool
async def get_route_tool(params: FunctionCallParams, origin: str, destination: str, travel_mode: str = "DRIVE"):
    """Calculates the shortest distance and travel duration between origin and destination given mode of transport.

    Args:
        origin: The starting location string (e.g., 'Taipei 101' or 'New York City').
        destination: The destination string (e.g., 'Hsinchu City' or 'Boston').
        travel_mode: Valid modes are 'DRIVE', 'BICYCLE', 'WALK', 'TWO_WHEELER', or 'TRANSIT'. Default is 'DRIVE'.
    """
    
    # utility call
    route_data = await utility.get_route(
        origin=origin, 
        destination=destination,
        travel_mode=travel_mode
    )
    
    # prune
    allowed_keys = {'distance_meters', 'duration'}
    pruned_data = pick_keys(route_data, allowed_keys)
    
    await params.result_callback(pruned_data)
    
def get_tools():
    return REGISTERED_TOOLS

