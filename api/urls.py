from django.urls import path
from .views import get_converted_amount

urlpatterns = [
    path('convert/<str:currency1>/<str:currency2>/<str:amount>/', get_converted_amount, name='convert-api'),
]
