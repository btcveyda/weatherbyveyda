#!/usr/bin/env python3
"""
Quick test script to verify the weather API.
To use with a real API key, update .env and run this script.
"""
import asyncio
import httpx
import json


async def main():
    base_url = "http://localhost:8000"
    
    print("=== Testing Weather API ===\n")
    
    # Test health
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{base_url}/health")
        print(f"✓ Health check: {resp.status_code}")
        print(f"  {json.dumps(resp.json(), indent=2)}\n")
        
        # Test weather (will fail with dummy API key, but shows structure)
        print("Testing weather endpoint (note: dummy API key will return 401):")
        resp = await client.get(f"{base_url}/weather", params={"city": "London"})
        print(f"Status: {resp.status_code}")
        print(f"Response:\n{json.dumps(resp.json(), indent=2)}\n")
        
        # Show what a successful response would look like
        print("Expected structure with valid API key:")
        example = {
            "city": "London",
            "country": "GB",
            "coordinates": {"lat": 51.5085, "lon": -0.1257},
            "temperature": {"celsius": 15.5, "fahrenheit": 59.9},
            "humidity": 72,
            "pressure": 1013,
            "weather": {"main": "Clouds", "description": "overcast clouds"},
            "wind": {"speed": 4.5, "deg": 230},
            "source": "openweathermap",
            "fetched_at": "2026-06-30T12:00:00.000000",
            "cached": False
        }
        print(json.dumps(example, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
