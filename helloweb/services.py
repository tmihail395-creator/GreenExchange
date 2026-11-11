import json
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

API_URL = "https://api.coingecko.com/api/v3/simple/price"

# (тикер, название, id в CoinGecko)
COINS = [
    ("BTC",  "Bitcoin",  "bitcoin"),
    ("ETH",  "Ethereum", "ethereum"),
    ("USDT", "Tether",   "tether"),
    ("BNB",  "BNB",      "binancecoin"),
    ("SOL",  "Solana",   "solana"),
    ("TON",  "Toncoin",  "the-open-network"),
    ("XRP",  "XRP",      "ripple"),
]

CACHE_KEY = "market_data"
CACHE_SECONDS = 600        # 5 минут: укладывается в бесплатный лимит
ERROR_CACHE_SECONDS = 120  # после ошибки не повторяем запрос слишком часто

# Запасные курсы, если API недоступен (условные значения)
FALLBACK_CRYPTO = [
    {"code": "BTC",  "name": "Bitcoin",  "price": 67250.00, "change": 2.4},
    {"code": "ETH",  "name": "Ethereum", "price": 3420.50,  "change": -1.1},
    {"code": "USDT", "name": "Tether",   "price": 1.00,     "change": 0.0},
    {"code": "BNB",  "name": "BNB",      "price": 585.30,   "change": 0.8},
    {"code": "SOL",  "name": "Solana",   "price": 165.40,   "change": 4.2},
    {"code": "TON",  "name": "Toncoin",  "price": 6.85,     "change": 1.9},
    {"code": "XRP",  "name": "XRP",      "price": 0.52,     "change": -0.6},
]
FALLBACK_FIAT = [
    {"code": "USD", "name": "US Dollar", "price": 1.0},
    {"code": "UAH", "name": "Hryvnia",   "price": 0.0241},
]


def _fetch():
    params = urllib.parse.urlencode({
        "ids": ",".join(c[2] for c in COINS),
        "vs_currencies": "usd,uah",
        "include_24hr_change": "true",
    })
    req = urllib.request.Request(
        API_URL + "?" + params,
        headers={
            "Accept": "application/json",
            "x-cg-demo-api-key": settings.COINGECKO_API_KEY,
        },
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        raw = json.loads(resp.read().decode("utf-8"))

    crypto = []
    for code, name, cg_id in COINS:
        item = raw[cg_id]
        crypto.append({
            "code": code,
            "name": name,
            "price": float(item["usd"]),
            "change": round(float(item.get("usd_24h_change") or 0), 2),
        })

    # курс гривни выводим из BTC: сколько UAH стоит 1 USD
    btc = raw["bitcoin"]
    usd_in_uah = float(btc["uah"]) / float(btc["usd"])
    fiat = [
        {"code": "USD", "name": "US Dollar", "price": 1.0},
        {"code": "UAH", "name": "Hryvnia",   "price": 1 / usd_in_uah},
    ]
    return crypto, fiat


def get_market():
    """Курсы из кеша или из API; при ошибке отдаёт запасные."""
    data = cache.get(CACHE_KEY)
    if data:
        return data

    try:
        crypto, fiat = _fetch()
        data = {"crypto": crypto, "fiat": fiat, "live": True, "updated": timezone.now()}
        cache.set(CACHE_KEY, data, CACHE_SECONDS)
    except Exception as e:
        print("CoinGecko error:", e)   # причина ошибки появится в консоли PyCharm
        data = {"crypto": FALLBACK_CRYPTO, "fiat": FALLBACK_FIAT, "live": False, "updated": None}
        cache.set(CACHE_KEY, data, ERROR_CACHE_SECONDS)
    return data