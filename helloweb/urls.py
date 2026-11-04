from django.urls import path
from . import views, charts

urlpatterns = [
    path('', views.index, name='index'),
    path('rates', views.rates, name='rates'),
    path('charts', charts.charts_page, name='charts'),
    path('charts/data/<str:code>/<int:days>', charts.chart_data, name='chart_data'),
    path('how-it-works', views.how, name='how'),
    path('faq', views.faq, name='faq'),
    path('contacts', views.contacts, name='contacts'),
]



