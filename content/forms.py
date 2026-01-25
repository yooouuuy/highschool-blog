from django import forms
from .models import Lesson, Test, Question, Announcement, Resource, ForumThread, ForumPost, LessonComment

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'year', 'stream', 'subject', 'pdf_file']

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'description', 'year', 'stream', 'subject', 'pdf_file']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content']

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'type', 'file', 'url', 'year', 'stream', 'subject']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-input'}),
            'year': forms.Select(attrs={'class': 'form-input'}),
            'stream': forms.Select(attrs={'class': 'form-input'}),
            'subject': forms.Select(attrs={'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        resource_type = cleaned_data.get('type')
        file = cleaned_data.get('file')
        url = cleaned_data.get('url')

        if resource_type == 'pdf' and not file:
            self.add_error('file', 'You must upload a PDF file.')
        
        if resource_type in ['video', 'link'] and not url:
            self.add_error('url', 'You must provide a URL.')
            
        return cleaned_data

class ForumThreadForm(forms.ModelForm):
    class Meta:
        model = ForumThread
        fields = ['title', 'category', 'year', 'stream', 'subject']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'year': forms.Select(attrs={'class': 'form-input'}),
            'stream': forms.Select(attrs={'class': 'form-input'}),
        }

class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Write your reply...'}),
        }

class LessonCommentForm(forms.ModelForm):
    class Meta:
        model = LessonComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Ask a question or leave a comment...'}),
        }
