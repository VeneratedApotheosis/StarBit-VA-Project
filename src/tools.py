import asyncio

from pipecat.adapters.schemas.direct_function import tool_options
from pipecat.services.llm_service import FunctionCallParams

@tool_options(cancel_on_interruption=True, timeout_secs=30)
async def get_current_weather(params: FunctionCallParams, location: str, format: str):
    """Get the current weather.

    Args:
        location: The city and state, e.g. "San Francisco, CA".
        format: The temperature unit to use. Must be either "celsius" or "fahrenheit". Infer this from the user's location.
    """
    # Simulate a long-running API call.
    await asyncio.sleep(1)
    await params.result_callback({"conditions": "nice", "temperature": "75"})

@tool_options(cancel_on_interruption=True, timeout_secs=30)
async def test_tool_1(params: FunctionCallParams):
    """Test tool 1, returns a specific string to validate the tool calling

    Args:
        No args.
    """

    await asyncio.sleep(1)
    await params.result_callback({"result": "10012"})

@tool_options(cancel_on_interruption=True, timeout_secs=30)
async def test_tool_2(params: FunctionCallParams):
    """Test tool 2, returns a specific string to validate the tool calling

    Args:
        No args.
    """

    await asyncio.sleep(1)
    await params.result_callback({"result": "50052"})


def get_tools():
    return [get_current_weather]

def get_test_tools():
    return [test_tool_1, test_tool_2]