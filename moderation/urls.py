from django.urls import path
from . import views

app_name = 'moderation'

urlpatterns = [
    path('report/<int:content_type_id>/<int:object_id>/', views.ReportCreateView.as_view(), name='report_create'),
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('action/<int:report_id>/', views.ModerationActionView.as_view(), name='report_action'),
]
