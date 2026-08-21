import aiohttp
import asyncio
from typing import Optional, Dict, Any

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
#                                  Boilerplate                                 #
# ---------------------------------------------------------------------------- #    
async def fetch_json(url: str, params: dict, timeout_secs: float = 5.0) -> Dict[str, Any]:
    """
    Generic HTTP GET boilerplate    . 
    Returns the parsed JSON dictionary, or an error dictionary if it fails.
    """
    session = await get_shared_session()
    
    try:
        timeout = aiohttp.ClientTimeout(total=timeout_secs)
        async with session.get(url, params=params, timeout=timeout) as response:
            response.raise_for_status()
            return await response.json()
            
    except asyncio.TimeoutError:
        return {"error": "API request timed out."}
    except Exception as e:
        return {"error": f"API request failed: {str(e)}"}

# ---------------------------------------------------------------------------- #
#                                   Api Funcs                                  #
# ---------------------------------------------------------------------------- #
async def get_geocode(place: str, count: int = 1) -> dict:
    """Searches for geographic information given a location name."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": place,
        "count": count,
    }
    # fetch
    data = await fetch_json(url, params)
    
    # error checking
    if "error" in data:
        return data
        
    # data parsing
    if "results" in data and len(data["results"]) > 0:
        return data["results"][0]
    
    return {"error": f"No location coordinates found for '{place}'."}
    
# ---------------------------------------------------------------------------- #
#                                     debug                                    #
# ---------------------------------------------------------------------------- #
async def mainfr():
    try:
        local = await get_geocode("paris")
        print(local)
    finally:
        # Properly close connections before exiting
        await close_shared_session()

asyncio.run(mainfr())