from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/', include('apps.companies.urls')),
    path('api/', include('apps.templates.urls')),
    path('api/', include('apps.audits.urls')),
    path('api/', include('apps.dashboard.urls')),
    path('api/', include('apps.comparisons.urls')),
    path('api/', include('apps.teams.urls')),
]
