from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ComparisonViewSet,
    RecommendationViewSet,
    CompareAuditsView,
    TrendsAnalysisView,
    GenerateRecommendationsView,
    AuditRecommendationsView
)

app_name = 'comparisons'

router = DefaultRouter()
router.register(r'comparisons', ComparisonViewSet, basename='comparison')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')

urlpatterns = [
    path('', include(router.urls)),
    path('comparisons/compare/', CompareAuditsView.as_view(), name='compare'),
    path('comparisons/trends/', TrendsAnalysisView.as_view(), name='trends'),
    path('audits/<int:audit_id>/generate-recommendations/', GenerateRecommendationsView.as_view(), name='generate_recommendations'),
    path('audits/<int:audit_id>/recommendations/', AuditRecommendationsView.as_view(), name='audit_recommendations'),
]
