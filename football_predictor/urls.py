"""
URL configuration for football_predictor project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('system-core-database/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Google OAuth URLs
    path('', include('predictor.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


