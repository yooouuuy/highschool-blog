from django.urls import path
from . import views, admin_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('registration-pending/', views.registration_pending, name='registration_pending'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.teacher_profile, name='teacher_profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/pending/', admin_views.pending_users, name='pending_users'),
    path('users/approve/<int:pk>/', admin_views.approve_user, name='approve_user'),
]
