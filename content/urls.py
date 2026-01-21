from django.urls import path
from . import views

urlpatterns = [
    path('lessons/', views.lesson_list, name='lesson_list'),
    path('lessons/create/', views.lesson_create, name='lesson_create'),
    path('lessons/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('tests/create/', views.test_create, name='test_create'),
    path('tests/<int:pk>/', views.test_detail, name='test_detail'),
    path('tests/<int:test_pk>/add_question/', views.question_add, name='question_add'),
    path('tests/<int:pk>/take/', views.take_test, name='take_test'),
    path('results/<int:pk>/', views.result_detail, name='result_detail'),
    path('tests/', views.test_list, name='test_list'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('lessons/pending/', views.pending_lessons, name='pending_lessons'),
    path('lessons/approve/<int:pk>/', views.approve_lesson, name='approve_lesson'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    path('announcements/delete/<int:pk>/', views.delete_announcement, name='delete_announcement'),
    path('chat/<int:year>/<str:stream>/', views.chat_room, name='chat_room'),
    path('chat/<int:year>/<str:stream>/send/', views.send_message, name='send_message'),
    path('chat/<int:year>/<str:stream>/messages/', views.get_messages, name='get_messages'),
]
