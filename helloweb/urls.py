from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('rates', views.rates, name='rates'),
    path('how-it-works', views.how, name='how'),
    path('faq', views.faq, name='faq'),
    path('contacts', views.contacts, name='contacts'),
]



