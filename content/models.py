from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from users.models import YEAR_CHOICES, STREAM_CHOICES, SUBJECT_CHOICES

class Lesson(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    content = models.TextField(_('Content'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lessons', verbose_name=_('Author'))
    year = models.IntegerField(_('Year'), choices=YEAR_CHOICES, null=True, blank=True)
    stream = models.CharField(_('Stream'), max_length=50, choices=STREAM_CHOICES, null=True, blank=True)
    subject = models.CharField(_('Subject'), max_length=50, choices=SUBJECT_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_approved = models.BooleanField(_('Is Approved'), default=False)
    is_removed = models.BooleanField(_('Is Removed'), default=False)
    pdf_file = models.FileField(_('PDF File'), upload_to='lessons/pdfs/', null=True, blank=True)


    def __str__(self):
        return self.title

class Announcement(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    content = models.TextField(_('Content'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Author'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_removed = models.BooleanField(_('Is Removed'), default=False)


    def __str__(self):
        return self.title

class Test(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tests', verbose_name=_('Author'))
    year = models.IntegerField(_('Year'), choices=YEAR_CHOICES, null=True, blank=True)
    stream = models.CharField(_('Stream'), max_length=50, choices=STREAM_CHOICES, null=True, blank=True)
    subject = models.CharField(_('Subject'), max_length=50, choices=SUBJECT_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_approved = models.BooleanField(_('Is Approved'), default=False)
    is_removed = models.BooleanField(_('Is Removed'), default=False)
    pdf_file = models.FileField(_('PDF File'), upload_to='tests/pdfs/', null=True, blank=True)


    def __str__(self):
        return self.title

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions', verbose_name=_('Test'))
    text = models.CharField(_('Question Text'), max_length=500)
    option_a = models.CharField(_('Option A'), max_length=200)
    option_b = models.CharField(_('Option B'), max_length=200)
    option_c = models.CharField(_('Option C'), max_length=200)
    option_d = models.CharField(_('Option D'), max_length=200)
    correct_option = models.CharField(_('Correct Option'), max_length=1, choices=[

        ('A', _('Option A')),
        ('B', _('Option B')),
        ('C', _('Option C')),
        ('D', _('Option D')),
    ])
    is_removed = models.BooleanField(_('Is Removed'), default=False)

    def __str__(self):
        return f"{self.text[:50]}..."

class Result(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='results', verbose_name=_('Student'))
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results', verbose_name=_('Test'))
    score = models.IntegerField(_('Score'))
    total_questions = models.IntegerField(_('Total Questions'))
    date_taken = models.DateTimeField(_('Date Taken'), auto_now_add=True)
    teacher_feedback = models.TextField(_('Teacher Feedback'), null=True, blank=True)
    feedback_date = models.DateTimeField(_('Feedback Date'), null=True, blank=True)


    def __str__(self):
        return f"{self.student.username} - {self.test.title} - {self.score}/{self.total_questions}"

class ChatMessage(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Author'))
    year = models.IntegerField(_('Year'), choices=YEAR_CHOICES)
    stream = models.CharField(_('Stream'), max_length=50, choices=STREAM_CHOICES)
    message = models.TextField(_('Message'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_removed = models.BooleanField(_('Is Removed'), default=False)


    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['year', 'stream', 'created_at']),
        ]

    def __str__(self):
        return f"{self.author.username} - Year {self.year} {self.stream} - {self.created_at}"

class Resource(models.Model):
    RESOURCE_TYPES = [
        ('pdf', _('PDF Document')),
        ('video', _('Video Link')),
        ('link', _('External Link')),
    ]
    title = models.CharField(_('Title'), max_length=200)
    type = models.CharField(_('Type'), max_length=10, choices=RESOURCE_TYPES)
    file = models.FileField(_('File'), upload_to='resources/files/', null=True, blank=True)
    url = models.URLField(_('URL'), null=True, blank=True)
    year = models.IntegerField(_('Year'), choices=YEAR_CHOICES, null=True, blank=True)
    stream = models.CharField(_('Stream'), max_length=50, choices=STREAM_CHOICES, null=True, blank=True)
    subject = models.CharField(_('Subject'), max_length=50, choices=SUBJECT_CHOICES, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Author'))
    is_approved = models.BooleanField(_('Is Approved'), default=False)
    is_removed = models.BooleanField(_('Is Removed'), default=False)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)


    def __str__(self):
        return self.title

class ForumThread(models.Model):
    CATEGORY_CHOICES = [
        ('question', _('Question')),
        ('discussion', _('General Discussion')),
        ('resource', _('Resource Share')),
    ]
    
    title = models.CharField(_('Title'), max_length=200)
    category = models.CharField(_('Category'), max_length=20, choices=CATEGORY_CHOICES, default='discussion')
    subject = models.CharField(_('Subject'), max_length=50, choices=SUBJECT_CHOICES)
    year = models.IntegerField(_('Year'), choices=YEAR_CHOICES, null=True, blank=True)
    stream = models.CharField(_('Stream'), max_length=50, choices=STREAM_CHOICES, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Author'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_removed = models.BooleanField(_('Is Removed'), default=False)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class ForumPost(models.Model):
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='posts', verbose_name=_('Thread'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Author'))
    content = models.TextField(_('Content'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_removed = models.BooleanField(_('Is Removed'), default=False)


    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Post by {self.author.username} on {self.thread.title}"


class LessonComment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Lesson'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Author'))
    content = models.TextField(_('Content'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_removed = models.BooleanField(_('Is Removed'), default=False)


    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.lesson.title}"

class StudentAnswer(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='answers', verbose_name=_('Result'))
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_('Question'))
    selected_option = models.CharField(_('Selected Option'), max_length=1)
    is_correct = models.BooleanField(_('Is Correct'), default=False)


    def __str__(self):
        return f"{self.result.student.username} - {self.question.id} - {self.is_correct}"

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name=_('Recipient'))
    announcement = models.ForeignKey('Announcement', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', verbose_name=_('Announcement'))
    title = models.CharField(_('Title'), max_length=255)
    message = models.TextField(_('Message'))
    link = models.CharField(_('Link'), max_length=255, blank=True, null=True)
    is_read = models.BooleanField(_('Is Read'), default=False)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_removed = models.BooleanField(_('Is Removed'), default=False)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"
