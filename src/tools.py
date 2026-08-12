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


def get_tools():
    return [get_current_weather]