import asyncio
import aiohttp

API_KEY = "replace when testing"

async def check_modern_key():
    async with aiohttp.ClientSession() as session:
        
        # 1. Routes API (Replaces Directions & Distance Matrix)
        routes_url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        routes_headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": API_KEY,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters",
        }
        routes_body = {
            "origin": {"address": "Taipei"},
            "destination": {"address": "Kaohsiung"},
            "travelMode": "DRIVE",
        }
        
        # 2. Places API (New)
        places_url = "https://places.googleapis.com/v1/places:searchText"
        places_headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": API_KEY,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress",
        }
        places_body = {"textQuery": "coffee in Taipei"}

        # 3. Address Validation API
        addr_url = f"https://addressvalidation.googleapis.com/v1:validateAddress?key={API_KEY}"
        addr_body = {"address": {"addressLines": ["1600 Amphitheatre Pkwy, Mountain View, CA"]}}

        tests = [
            ("Routes API (v2)", routes_url, "POST", routes_headers, routes_body),
            ("Places API (New)", places_url, "POST", places_headers, places_body),
            ("Address Validation API", addr_url, "POST", {"Content-Type": "application/json"}, addr_body),
        ]

        for name, url, method, headers, body in tests:
            async with session.request(method, url, headers=headers, json=body) as resp:
                data = await resp.json()
                if resp.status == 200:
                    print(f"✅ ENABLED: {name}")
                else:
                    error_msg = data.get("error", {}).get("message", "Request Failed")
                    print(f"❌ DISABLED: {name} (HTTP {resp.status}: {error_msg})")

asyncio.run(check_modern_key())