from core.mcp_client import create_mcp_client
from tools.local_tools import get_local_tools


def get_static_tools() -> list:
    """fetch all locally dec tools"""
    return get_local_tools()


async def get_mcp_tools() -> list:
    """async fetch dynamic mcp tool from server"""
    mcp_client = create_mcp_client()
    return await mcp_client.tools()


async def get_all_tools() -> list:
    """returns static + mcp tools"""
    tools = get_static_tools()
    mcp_tools = await get_mcp_tools()
    tools.extend(mcp_tools)
    return tools