from django.contrib.auth import views as auth_views
from django.urls import path

from . import views, charts, news
from .forms import LoginForm

urlpatterns = [
    path('', views.index, name='index'),
    path('rates', views.rates, name='rates'),
    path('charts', charts.charts_page, name='charts'),
    path('charts/data/<str:code>/<int:days>', charts.chart_data, name='chart_data'),

    path('news', news.news_list, name='news'),
    path('news/submit', news.news_submit, name='news_submit'),
    path('news/mine', news.news_mine, name='news_mine'),
    path('news/<int:pk>', news.news_detail, name='news_detail'),

    path('how-it-works', views.how, name='how'),
    path('faq', views.faq, name='faq'),
    path('contacts', views.contacts, name='contacts'),

    path('register', views.register, name='register'),
    path('login', auth_views.LoginView.as_view(
        template_name='helloweb/login.html',
        authentication_form=LoginForm,
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
]



