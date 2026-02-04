from django.urls import path
from .views import DashboardView, UserManagementView, ContentManagementView, ActionView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('users/', UserManagementView.as_view(), name='users'),
    path('content/', ContentManagementView.as_view(), name='content'),
    path('action/', ActionView.as_view(), name='action'),
]
