from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_home, name='admin_home'),
    path('all_trans/', views.transactions_all, name='all_transactions'),
    path('all_requests/', views.request_all, name='all_requests'),
    path('all_users/', views.users_all, name='all_users'),
    path('register_admin/', views.admin_create, name='Create_super')

]
