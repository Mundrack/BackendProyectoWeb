from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TeamViewSet,
    TeamMemberViewSet,
    HierarchyView,
    EmployeeTeamsView
)

app_name = 'teams'

router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'team-members', TeamMemberViewSet, basename='team_member')

urlpatterns = [
    path('', include(router.urls)),
    path('teams/hierarchy/', HierarchyView.as_view(), name='hierarchy'),
    path('employees/<int:user_id>/teams/', EmployeeTeamsView.as_view(), name='employee_teams'),
]
