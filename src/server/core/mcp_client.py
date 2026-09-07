from pipecat.services.mcp_service import MCPClient
from mcp.client.session_group import StreamableHttpParameters
from config import config

def create_mcp_client() -> MCPClient:
    """Init native pipecat mcp client"""
    server_params = StreamableHttpParameters(url=config.mcp_url)
    return MCPClient(server_params=server_params)