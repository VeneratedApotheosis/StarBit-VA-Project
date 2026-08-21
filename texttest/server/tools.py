import asyncio
from pipecat.adapters.schemas.direct_function import tool_options
from pipecat.services.llm_service import FunctionCallParams
import texttest.server.get_current_time as http_client

REGISTERED_TOOLS = []

def register_tool(func):
    REGISTERED_TOOLS.append(func)
    return func

# ---------------------------------------------------------------------------- #
#                                     Tools                                    #
# ---------------------------------------------------------------------------- #
@register_tool
@tool_options(cancel_on_interruption=False, timeout_secs=30)
async def get_time_tool(params: FunctionCallParams):
    """Gets the current time from computer"""
    current_time = await http_client.get_current_time()
    await params.result_callback({"current_time": current_time})
    
# @register_tool
@tool_options(cancel_on_interruption=False, timeout_secs=30)
async def get_weather_tool(params: FunctionCallParams, place: str):
    """Gets weather at a location given location name

    Args:
        place: location name string to query weather from
    """

    await asyncio.sleep(1)
    await params.result_callback({"weather" : "sunny"})

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
