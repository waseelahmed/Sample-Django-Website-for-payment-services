from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('home', views.home, name='home'),
    path('transactions', views.transaction_history, name='Transaction_History'),
    path('profile', views.profile, name='Profile'),
    path('pay_money', views.pay_money, name='Send'),
    path('request_money', views.request_money, name='Request'),
    path('request_history', views.request_history, name='Request_History'),
    path('ws/notifications/', include('notifications.urls')),
]
