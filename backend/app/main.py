import asyncio
import os
from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from .config import settings
from .cache import get_cache

app = FastAPI(title="Weather API")
CACHE = get_cache()


async def fetch_weather_from_api(city: str) -> dict:
    if not settings.OPENWEATHER_API_KEY:
        raise RuntimeError("OPENWEATHER_API_KEY not set")
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": settings.OPENWEATHER_API_KEY, "units": "metric"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Upstream error: {resp.status_code} {resp.text}")
        return resp.json()


def map_openweather_to_standard(data: dict) -> dict:
    # Map relevant fields into a consistent response
    coord = data.get("coord", {})
    sys = data.get("sys", {})
    main = data.get("main", {})
    weather_list = data.get("weather", [])
    weather = weather_list[0] if weather_list else {}
    wind = data.get("wind", {})

    temp_c = main.get("temp")
    temp_f = None
    if temp_c is not None:
        temp_f = temp_c * 9 / 5 + 32

    return {
        "city": data.get("name"),
        "country": sys.get("country"),
        "coordinates": {"lat": coord.get("lat"), "lon": coord.get("lon")},
        "temperature": {"celsius": temp_c, "fahrenheit": temp_f},
        "humidity": main.get("humidity"),
        "pressure": main.get("pressure"),
        "weather": {"main": weather.get("main"), "description": weather.get("description")},
        "wind": {"speed": wind.get("speed"), "deg": wind.get("deg")},
        "source": "openweathermap",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "now": datetime.utcnow().isoformat()}


@app.get("/weather")
async def get_weather(city: str = Query(..., min_length=1)):
    key = f"weather:{city.lower().strip()}"
    try:
        cached = await CACHE.get(key)
        if cached:
            cached["cached"] = True
            return JSONResponse(status_code=200, content=cached)

        data = await fetch_weather_from_api(city)
        mapped = map_openweather_to_standard(data)
        payload = {"fetched_at": datetime.utcnow().isoformat(), **mapped}
        await CACHE.set(key, payload, settings.CACHE_TTL)
        payload["cached"] = False
        return JSONResponse(status_code=200, content=payload)
    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.FASTAPI_HOST, port=settings.FASTAPI_PORT)
