from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from users.models import YEAR_CHOICES, STREAM_CHOICES, SUBJECT_CHOICES

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lessons')
    year = models.IntegerField(choices=YEAR_CHOICES, null=True, blank=True)
    stream = models.CharField(max_length=50, choices=STREAM_CHOICES, null=True, blank=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to='lessons/pdfs/', null=True, blank=True)

    def __str__(self):
        return self.title

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Test(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tests')
    year = models.IntegerField(choices=YEAR_CHOICES, null=True, blank=True)
    stream = models.CharField(max_length=50, choices=STREAM_CHOICES, null=True, blank=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to='tests/pdfs/', null=True, blank=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1, choices=[
        ('A', _('Option A')),
        ('B', _('Option B')),
        ('C', _('Option C')),
        ('D', _('Option D')),
    ])

    def __str__(self):
        return f"{self.text[:50]}..."

class Result(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='results')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    score = models.IntegerField()
    total_questions = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)
    teacher_feedback = models.TextField(null=True, blank=True)
    feedback_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.test.title} - {self.score}/{self.total_questions}"

class ChatMessage(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    year = models.IntegerField(choices=YEAR_CHOICES)
    stream = models.CharField(max_length=50, choices=STREAM_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username} - Year {self.year} {self.stream} - {self.created_at}"

class Resource(models.Model):
    RESOURCE_TYPES = [
        ('pdf', _('PDF Document')),
        ('video', _('Video Link')),
        ('link', _('External Link')),
    ]
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='resources/files/', null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    year = models.IntegerField(choices=YEAR_CHOICES, null=True, blank=True)
    stream = models.CharField(max_length=50, choices=STREAM_CHOICES, null=True, blank=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ForumThread(models.Model):
    CATEGORY_CHOICES = [
        ('question', _('Question')),
        ('discussion', _('General Discussion')),
        ('resource', _('Resource Share')),
    ]
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='discussion')
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    year = models.IntegerField(choices=YEAR_CHOICES, null=True, blank=True)
    stream = models.CharField(max_length=50, choices=STREAM_CHOICES, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class ForumPost(models.Model):
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Post by {self.author.username} on {self.thread.title}"


class LessonComment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.lesson.title}"

class StudentAnswer(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.result.student.username} - {self.question.id} - {self.is_correct}"

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    announcement = models.ForeignKey('Announcement', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
