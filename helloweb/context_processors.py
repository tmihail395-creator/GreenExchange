from .models import News
from .services import get_market


def market(request):
    """Курсы доступны во всех шаблонах, а админам ещё и счётчик заявок на новости."""
    m = get_market()
    ctx = {
        "ticker": m["crypto"][:5],
        "market_live": m["live"],
        "market_updated": m["updated"],
    }

    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated and user.is_staff:
        ctx["pending_news"] = News.objects.filter(status=News.Status.PENDING).count()

    return ctx