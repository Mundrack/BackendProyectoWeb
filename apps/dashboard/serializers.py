from rest_framework import serializers


class OverviewStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas generales del dashboard"""
    total_audits = serializers.IntegerField()
    audits_in_progress = serializers.IntegerField()
    completed_audits = serializers.IntegerField()
    average_score = serializers.FloatField()
    total_companies = serializers.IntegerField()
    total_branches = serializers.IntegerField()
    completion_rate = serializers.FloatField()


class AuditTrendSerializer(serializers.Serializer):
    """Serializer para tendencias de auditorías por período"""
    period = serializers.CharField()
    total = serializers.IntegerField()
    completed = serializers.IntegerField()
    avg_score = serializers.FloatField()


class RecentAuditSerializer(serializers.Serializer):
    """Serializer para auditorías recientes"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    company_name = serializers.CharField()
    branch_name = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    score_percentage = serializers.FloatField()
    created_at = serializers.CharField()
    completed_at = serializers.CharField(allow_null=True)


class CompanyStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas por empresa"""
    company_id = serializers.IntegerField()
    company_name = serializers.CharField()
    total_audits = serializers.IntegerField()
    completed = serializers.IntegerField()
    avg_score = serializers.FloatField()
    branches_count = serializers.IntegerField()


class ScoreDistributionSerializer(serializers.Serializer):
    """Serializer para distribución de puntajes"""
    range = serializers.CharField()
    count = serializers.IntegerField()


class TemplateStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de uso de plantillas"""
    template_id = serializers.IntegerField()
    template_name = serializers.CharField()
    total_audits = serializers.IntegerField()
    completed = serializers.IntegerField()
    avg_score = serializers.FloatField()


class TopBranchSerializer(serializers.Serializer):
    """Serializer para mejores sucursales"""
    branch_id = serializers.IntegerField()
    branch_name = serializers.CharField()
    company_name = serializers.CharField()
    total_audits = serializers.IntegerField()
    avg_score = serializers.FloatField()


class PeriodAuditSerializer(serializers.Serializer):
    """Serializer para auditoría dentro de un período"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    company_name = serializers.CharField()
    status = serializers.CharField()
    score_percentage = serializers.FloatField()
    created_at = serializers.CharField()


class PeriodStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas del período actual"""
    period = serializers.CharField()
    total = serializers.IntegerField()
    completed = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    draft = serializers.IntegerField()
    avg_score = serializers.FloatField()
    audits = PeriodAuditSerializer(many=True)


class CategoryPerformanceSerializer(serializers.Serializer):
    """Serializer para rendimiento por categoría"""
    category = serializers.CharField()
    total_responses = serializers.IntegerField()
    avg_score = serializers.FloatField()
    max_possible_avg = serializers.FloatField()
    percentage = serializers.FloatField()


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer completo combinando todas las estadísticas"""
    overview = OverviewStatsSerializer()
    recent_audits = RecentAuditSerializer(many=True)
    company_stats = CompanyStatsSerializer(many=True)
    score_distribution = ScoreDistributionSerializer(many=True)
    template_stats = TemplateStatsSerializer(many=True)
    top_branches = TopBranchSerializer(many=True)
    category_performance = CategoryPerformanceSerializer(many=True)
