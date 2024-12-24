from django.contrib import admin
from django.urls import path, include


# Override the admin login URL

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__reload__', include('django_browser_reload.urls')),
    path('',include('polls.urls')),
]
