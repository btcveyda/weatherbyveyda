# WeatherByVeyda

Simple FastAPI backend that fetches weather from OpenWeatherMap with caching, plus a minimal Django UI.

Prereqs:
- Python 3.11+
- (optional) Redis for caching

Setup:

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and set `OPENWEATHER_API_KEY`.

3. Run Redis (optional):

```bash
# using docker
docker run -p 6379:6379 -d redis:7
```

4. Start the FastAPI backend:

```bash
# from repository root
uvicorn backend.app.main:app --reload
# or using Python module
python -m uvicorn backend.app.main:app --reload
```

5. Start the Django UI (serves a simple page that calls the FastAPI endpoint from the browser):

```bash
cd webui
python manage.py runserver 8001
```

Usage:
- Visit http://127.0.0.1:8001 and enter a city.
- Or call the API directly: `GET http://127.0.0.1:8000/weather?city=London`

Notes:
- Caching: attempts to use `REDIS_URL` from environment; falls back to an in-memory cache with 10 minute TTL.
- The FastAPI app uses `httpx` for async requests.
- Error handling returns 502 for upstream errors and 500 for internal issues.

