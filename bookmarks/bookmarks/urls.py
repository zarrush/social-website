from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from account import views as account_views  # import view landing

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Landing Page روی صفحه اصلی
    path('', account_views.landing, name='landing'),
    
    # بقیه URLهای account
    path('account/', include('account.urls')),
]

# Serve media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)