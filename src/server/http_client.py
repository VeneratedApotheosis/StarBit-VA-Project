import aiohttp
from typing import Optional

# ---------------------------------------------------------------------------- #
#                                Shared Session                                #
# ---------------------------------------------------------------------------- #
_shared_session: Optional[aiohttp.ClientSession] = None

async def get_shared_session() -> aiohttp.ClientSession:
    global _shared_session
    if _shared_session is None or _shared_session.closed:
        _shared_session = aiohttp.ClientSession()
    return _shared_session

async def close_shared_session():
    global _shared_session
    if _shared_session and not _shared_session.closed:
        await _shared_session.close()

# ---------------------------------------------------------------------------- #
#                               actual functions                               #
# ---------------------------------------------------------------------------- #
async def fetch_json(url: str, params: dict, timeout_secs: float = 5.0) -> dict:
    session = await get_shared_session()
    timeout = aiohttp.ClientTimeout(total=timeout_secs)
    
    async with session.get(url, params=params, timeout=timeout) as response:
        response.raise_for_status()  # Raises aiohttp.ClientResponseError for 4xx/5xx
        return await response.json()
    
async def post_json(url: str, headers: dict, json_payload: dict, timeout_secs: float = 5.0) -> dict:
    session = await get_shared_session()
    timeout = aiohttp.ClientTimeout(total=timeout_secs)
    
    async with session.post(url, headers=headers, json=json_payload, timeout=timeout) as response:
        response.raise_for_status()
        return await response.json()