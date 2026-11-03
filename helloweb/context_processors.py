from .services import get_market


def market(request):
    """Курсы доступны во всех шаблонах сайта."""
    m = get_market()
    return {
        "ticker": m["crypto"][:5],
        "market_live": m["live"],
        "market_updated": m["updated"],
    }