from django.urls import path, include
from . import views

urlpatterns = [
    # --- احراز هویت ---
    path('', include('django.contrib.auth.urls')),
    
    # --- کاربر و پروفایل ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('edit/', views.edit, name='edit'),
    
    # --- پست‌ها ---
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/like/', views.post_like, name='post_like'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    
    # --- کاربران و فالو ---
    path('users/', views.user_list, name='user_list'),
    path('users/<str:username>/', views.user_profile, name='user_profile'),
    path('users/<int:user_id>/follow/', views.user_follow, name='user_follow'),
]