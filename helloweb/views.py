from django.shortcuts import render
from .services import get_market


def index(request):
    m = get_market()
    return render(request, 'helloweb/index.html', {
        'rates': m['crypto'][:5],
        'assets': m['crypto'] + m['fiat'],
        'live': m['live'],
        'updated': m['updated'],
    })


def rates(request):
    m = get_market()
    return render(request, 'helloweb/rates.html', {
        'rates': m['crypto'],
        'live': m['live'],
        'updated': m['updated'],
    })


def how(request):
    return render(request, 'helloweb/how.html')


def faq(request):
    return render(request, 'helloweb/faq.html')


def contacts(request):
    return render(request, 'helloweb/contacts.html')