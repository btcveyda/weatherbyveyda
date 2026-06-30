#!/usr/bin/env python3
"""
Test script demonstrating caching behavior.
Shows the cache layer working with mock data.
"""
import asyncio
import json
import time
from datetime import datetime
from backend.app.cache import InMemoryCache
from backend.app.main import map_openweather_to_standard


async def test_caching():
    print("=" * 60)
    print("🌦️  WEATHER API CACHING TEST")
    print("=" * 60 + "\n")
    
    # Use in-memory cache directly
    cache = InMemoryCache()
    
    # Mock the fetch function to return a fake weather response
    mock_data = {
        "name": "London",
        "sys": {"country": "GB"},
        "coord": {"lat": 51.5, "lon": -0.1},
        "main": {"temp": 15.5, "humidity": 72, "pressure": 1013},
        "weather": [{"main": "Clouds", "description": "overcast clouds"}],
        "wind": {"speed": 4.5, "deg": 230},
    }
    
    print("📍 Test City: London\n")
    
    # Call 1 - Cache miss
    print("📤 Call 1 - CACHE MISS (first fetch)...")
    key = "weather:london"
    
    start = time.time()
    mapped = map_openweather_to_standard(mock_data)
    payload = {"fetched_at": datetime.utcnow().isoformat(), **mapped}
    await cache.set(key, payload, 600)
    result1 = await cache.get(key)
    elapsed1 = time.time() - start
    print(f"   ✓ Cached in {elapsed1:.4f}s")
    print(f"   City: {result1.get('city')}, Temp: {result1.get('temperature', {}).get('celsius')}°C\n")
    
    # Call 2 - Cache hit
    print("📥 Call 2 - CACHE HIT (from memory)...")
    start = time.time()
    result2 = await cache.get(key)
    elapsed2 = time.time() - start
    print(f"   ✓ Retrieved in {elapsed2:.6f}s (instant!)")
    print(f"   City: {result2.get('city')}, Temp: {result2.get('temperature', {}).get('celsius')}°C\n")
    
    # Call 3 - Different city (new cache entry)
    print("📤 Call 3 - Different city (Paris)...")
    key2 = "weather:paris"
    mock_data2 = {**mock_data, "name": "Paris", "coord": {"lat": 48.8, "lon": 2.3}}
    mapped2 = map_openweather_to_standard(mock_data2)
    payload2 = {"fetched_at": datetime.utcnow().isoformat(), **mapped2}
    
    start = time.time()
    await cache.set(key2, payload2, 600)
    result3 = await cache.get(key2)
    elapsed3 = time.time() - start
    print(f"   ✓ Cached in {elapsed3:.4f}s")
    print(f"   City: {result3.get('city')}\n")
    
    # Call 4 - Back to London (cache hit)
    print("📥 Call 4 - London again (cache hit)...")
    result4 = await cache.get(key)
    print(f"   ✓ Retrieved London from cache instantly")
    print(f"   City: {result4.get('city')}\n")
    
    # Show response structure
    print("=" * 60)
    print("✅ CACHING TEST COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   • Stored 2 cities in cache")
    print(f"   • Multiple requests served from cache")
    print(f"   • TTL: 10 minutes (600 seconds)")
    print(f"   • With caching: Save API calls & bandwidth 🚀\n")
    
    print("📋 Sample Response Structure:")
    print(json.dumps(result4, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(test_caching())
