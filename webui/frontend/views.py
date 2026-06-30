from django.shortcuts import render
from django.conf import settings


def index(request):
    # FASTAPI_URL can be passed via template if needed
    fastapi_url = request.GET.get("fastapi_url", "http://127.0.0.1:8000")
    return render(request, "index.html", {"FASTAPI_URL": fastapi_url})
