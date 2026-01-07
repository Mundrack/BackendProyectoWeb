from django.urls import path
from .views import (
    DashboardOverviewView, AuditTrendsView, RecentAuditsView,
    CompanyStatsView, ScoreDistributionView, TemplateStatsView,
    TopBranchesView, PeriodStatsView, CategoryPerformanceView,
    DashboardSummaryView
)

urlpatterns = [
    # Dashboard endpoints
    path('dashboard/overview/', DashboardOverviewView.as_view(), name='dashboard-overview'),
    path('dashboard/trends/', AuditTrendsView.as_view(), name='dashboard-trends'),
    path('dashboard/recent-audits/', RecentAuditsView.as_view(), name='dashboard-recent-audits'),
    path('dashboard/company-stats/', CompanyStatsView.as_view(), name='dashboard-company-stats'),
    path('dashboard/score-distribution/', ScoreDistributionView.as_view(), name='dashboard-score-distribution'),
    path('dashboard/template-stats/', TemplateStatsView.as_view(), name='dashboard-template-stats'),
    path('dashboard/top-branches/', TopBranchesView.as_view(), name='dashboard-top-branches'),
    path('dashboard/period-stats/', PeriodStatsView.as_view(), name='dashboard-period-stats'),
    path('dashboard/category-performance/', CategoryPerformanceView.as_view(), name='dashboard-category-performance'),
    path('dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
]
