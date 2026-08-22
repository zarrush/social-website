from django.urls import path , include
from . import views
from django.contrib.auth import views as auth_views
from .views import dashboard, register, user_logout

urlpatterns = [
    path('images/', views.images, name='images'),
    path('people/', views.peoples, name='peoples'),

    path('', include('django.contrib.auth.urls')),
    path('', dashboard, name='dashboard'),
    path('register/', register, name='register'),
]
