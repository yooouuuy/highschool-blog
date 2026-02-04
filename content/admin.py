from django.contrib import admin
from .models import Lesson, Test, Question

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'year', 'stream', 'subject', 'created_at')
    list_filter = ('year', 'stream', 'subject', 'created_at', 'author')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'year', 'stream', 'subject', 'created_at')
    list_filter = ('year', 'stream', 'subject', 'created_at', 'author')
    search_fields = ('title', 'content')

admin.site.register(Question)
