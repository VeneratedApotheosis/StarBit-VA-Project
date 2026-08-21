import asyncio
import functools
import aiohttp
import utility
import http_client

from pipecat.adapters.schemas.direct_function import tool_options
from pipecat.services.llm_service import FunctionCallParams

REGISTERED_TOOLS = []
# ---------------------------------------------------------------------------- #
#                                  Boilerplate                                 #
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
        except Exception as e:
            match e:
                case utility.LocationNotFoundError():
                    error_msg = str(e)
                case asyncio.TimeoutError():
                    error_msg = "The service timed out while responding."
                case aiohttp.ClientError():
                    error_msg = "The external service is currently unreachable."
                case _:
                    error_msg = f"An unexpected error occurred: {str(e)}"
            
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
@tool_options(cancel_on_interruption=False, timeout_secs=30)
@safe_tool
async def get_time_tool(params: FunctionCallParams):
    """Gets the current time from computer"""
    current_time = await utility.get_current_time()
    formatted = {"current_time": current_time}
    await params.result_callback(formatted)
    
@register_tool
@tool_options(cancel_on_interruption=False, timeout_secs=30)
@safe_tool
async def get_geocode_tool(params: FunctionCallParams, place: str):
    """Searches for geographic coordinates (latitude and longitude) given a location name.
    
    Args:
        place: The name of the city, region, or landmark to geocode (e.g., 'Paris, France' or 'Tokyo').
    """
    raw_data = await utility.get_geocode(place=place)
    
    allowed_keys = {'name','longitude','latitude',}
    formatted = pick_keys(raw_data,allowed_keys)
    print(formatted)
    await params.result_callback(formatted)
    

# ---------------------------------------------------------------------------- #
#                                 Test / Debug                                 #
# ---------------------------------------------------------------------------- #
@register_tool
@tool_options(cancel_on_interruption=False, timeout_secs=30)
async def test_1_tool(params: FunctionCallParams):
    """a testing tool, returns a specific string to validate the tool calling"""

    await asyncio.sleep(1)
    await params.result_callback({"result": "10012"})


@register_tool
@tool_options(cancel_on_interruption=False, timeout_secs=30)
async def test_2_tool(params: FunctionCallParams):
    """a testing tool, returns a specific string to validate the tool calling"""

    await asyncio.sleep(1)
    await params.result_callback({"result": "50052"})

def get_tools():
    return REGISTERED_TOOLS
