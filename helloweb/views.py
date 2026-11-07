from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegisterForm
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


def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            if getattr(settings, 'REGISTRATION_REQUIRES_APPROVAL', False):
                user.is_active = False
                user.save()
                messages.success(
                    request,
                    "Account created. An administrator must approve it before you can log in.",
                )
                return redirect('login')

            user.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect('index')
    else:
        form = RegisterForm()

    return render(request, 'helloweb/register.html', {'form': form})