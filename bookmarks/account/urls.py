from django.urls import path
from django.contrib.auth import views as auth_views
from account.views import user_login
from .views import dashboard

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', dashboard, name='dashboard'),
]
