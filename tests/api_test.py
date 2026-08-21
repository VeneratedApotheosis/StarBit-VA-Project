import requests
import aiohttp
import asyncio

async def get_geocode(place : str):
    """Retrieves latitude and longitude coordinates for a given location name.

    Args:
        place: The city, address, or location name to search (e.g., "Paris", "Berlin").
    """    
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name" : place,
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                if "results" in data and len(data["results"]) > 0:
                    result = data["results"][0]
                else:
                    result = {"error": f"No location coordinates found for '{place}'."}

        except Exception as e:
            result = {"error": f"Geocoding request failed: {str(e)}"}

    return result

def get_weather(long : float, lat : float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": long,
        "longitude": lat,
        "current_weather": True
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    return data

async def handle_result(result):
    print("Result:", result)

async def main():
    print(await get_geocode(place="Tokyo"))

# Run the execution
asyncio.run(main())
