import json
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render

from .services import COINS, get_market

API_URL = "https://api.coingecko.com/api/v3/coins/{id}/market_chart"

COIN_IDS = {code: cg_id for code, name, cg_id in COINS}
ALLOWED_DAYS = [1, 7, 30, 90, 365]

CACHE_SECONDS = 900         # 15 минут: экономим лимит бесплатного ключа
ERROR_CACHE_SECONDS = 120
MAX_POINTS = 300            # больше точек на графике не нужно
CACHE_BY_DAYS = {1: 900, 7: 1800, 30: 3600, 90: 21600, 365: 21600}


def _downsample(points):
    if len(points) <= MAX_POINTS:
        return points
    step = -(-len(points) // MAX_POINTS)
    sampled = points[::step]
    if sampled[-1] != points[-1]:
        sampled.append(points[-1])
    return sampled


def _fetch_chart(cg_id, days):
    params = urllib.parse.urlencode({"vs_currency": "usd", "days": days})
    req = urllib.request.Request(
        API_URL.format(id=cg_id) + "?" + params,
        headers={
            "Accept": "application/json",
            "x-cg-demo-api-key": settings.COINGECKO_API_KEY,
        },
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        raw = json.loads(resp.read().decode("utf-8"))

    points = [[int(t), float(p)] for t, p in raw["prices"]]
    return _downsample(points)


def get_chart(code, days):
    """Точки графика из кеша или из API."""
    key = f"chart_{code}_{days}"
    data = cache.get(key)
    if data is not None:
        return data

    try:
        data = {"ok": True, "points": _fetch_chart(COIN_IDS[code], days)}
        cache.set(key, data, CACHE_BY_DAYS.get(days, 3600))
    except Exception as e:
        print("CoinGecko chart error:", e)   # причина появится в консоли PyCharm
        data = {"ok": False, "points": []}
        cache.set(key, data, ERROR_CACHE_SECONDS)
    return data


# ---------- Страница и данные для графика ----------

def charts_page(request):
    m = get_market()
    return render(request, 'helloweb/charts.html', {'coins': m['crypto']})


def chart_data(request, code, days):
    code = code.upper()
    if code not in COIN_IDS or days not in ALLOWED_DAYS:
        return JsonResponse({"error": "bad request"}, status=400)

    data = get_chart(code, days)
    if not data["ok"]:
        return JsonResponse({"error": "unavailable"}, status=503)

    return JsonResponse({"code": code, "days": days, "points": data["points"]})