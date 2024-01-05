from django.urls import path
from register import views as rg_view

urlpatterns = [
    path('user', rg_view.login_page, name="login"),
    path('register_user', rg_view.create_account, name='create user'),
    path('sign_in', rg_view.sign_in, name='signin'),
    path('sign_out', rg_view.sign_out, name='signout'),
    path('show_login_message', rg_view.show_login_message, name='show_login_message'),
    path('show_admin_error', rg_view.show_admin_error, name='show_admin_error'),

]
