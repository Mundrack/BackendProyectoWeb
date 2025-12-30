from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditTemplateViewSet, TemplateQuestionViewSet

app_name = 'templates'

router = DefaultRouter()
router.register(r'templates', AuditTemplateViewSet, basename='template')
router.register(r'questions', TemplateQuestionViewSet, basename='question')

urlpatterns = [
    path('', include(router.urls)),
]
