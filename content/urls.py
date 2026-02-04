from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_view, name='search'),
    path('lessons/', views.LessonListView.as_view(), name='lesson_list'),
    path('lessons/create/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('tests/create/', views.test_create, name='test_create'),
    path('tests/<int:pk>/', views.test_detail, name='test_detail'),
    path('tests/<int:test_pk>/add_question/', views.question_add, name='question_add'),
    path('tests/<int:pk>/take/', views.take_test, name='take_test'),
    path('results/<int:pk>/', views.result_detail, name='result_detail'),
    path('tests/', views.test_list, name='test_list'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),

    path('lessons/pending/', views.pending_lessons, name='pending_lessons'),
    path('lessons/approve/<int:pk>/', views.approve_lesson, name='approve_lesson'),
    path('tests/approve/<int:pk>/', views.approve_test, name='approve_test'),
    path('library/approve/<int:pk>/', views.approve_resource, name='approve_resource'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    path('announcements/delete/<int:pk>/', views.delete_announcement, name='delete_announcement'),
    path('chat/<int:year>/<str:stream>/', views.chat_room, name='chat_room'),
    path('chat/<int:year>/<str:stream>/send/', views.send_message, name='send_message'),
    path('chat/clear/', views.clear_chat_history, name='clear_chat_history'),
    path('chat/<int:year>/<str:stream>/messages/', views.get_messages, name='get_messages'),
    path('chat/message/edit/<int:pk>/', views.edit_chat_message, name='edit_chat_message'),
    path('chat/message/delete/<int:pk>/', views.delete_chat_message, name='delete_chat_message'),
    
    # Library
    path('library/', views.resource_list, name='resource_list'),
    path('library/create/', views.resource_create, name='resource_create'),
    
    # Forums
    path('forums/', views.forum_subjects, name='forum_subjects'),
    path('forums/<str:subject>/', views.forum_thread_list, name='forum_thread_list'),
    path('forums/thread/create/<str:subject>/', views.forum_thread_create, name='forum_thread_create'),
    path('forums/thread/<int:pk>/', views.forum_thread_detail, name='forum_thread_detail'),
    
    # Feedback
    
    # Deletion
    path('tests/analytics/<int:pk>/', views.test_analytics, name='test_analytics'),
    
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    
    # Deletion
    path('lessons/delete/<int:pk>/', views.delete_lesson, name='lesson_delete'),
    path('tests/delete/<int:pk>/', views.delete_test, name='test_delete'),
    path('forums/thread/delete/<int:pk>/', views.delete_forum_thread, name='forum_thread_delete'),
    path('library/delete/<int:pk>/', views.delete_resource, name='resource_delete'),
]
