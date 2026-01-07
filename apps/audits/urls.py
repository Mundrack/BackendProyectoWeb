from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditViewSet

app_name = 'audits'

router = DefaultRouter()
router.register(r'audits', AuditViewSet, basename='audit')

urlpatterns = [
    path('', include(router.urls)),
]
