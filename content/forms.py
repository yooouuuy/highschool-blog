from django import forms
from .models import Lesson, Test, Question, Announcement

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'year', 'stream', 'subject']

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'description', 'year', 'stream', 'subject']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content']
