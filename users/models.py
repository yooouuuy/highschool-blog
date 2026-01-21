from django.contrib.auth.models import AbstractUser
from django.db import models

YEAR_CHOICES = [
    (1, 'First Year'),
    (2, 'Second Year'),
    (3, 'Third Year'),
]

STREAM_CHOICES = [
    # First Year
    ('common_science', 'Common Science'),
    ('common_literature', 'Common Literature'),
    # Second & Third Year
    ('math', 'Math Stream'),
    ('science', 'Science Stream'),
    ('languages', 'Languages Stream'),
    ('literature', 'Literature Stream'),
    ('management_economics', 'Management & Economics Stream'),
    ('civil_engineering', 'Civil Engineering Stream'),
]

class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    
    real_name = models.CharField(max_length=100, default='')
    nickname = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    year = models.IntegerField(choices=YEAR_CHOICES, null=True, blank=True, help_text='Year level (for students)')
    stream = models.CharField(max_length=50, choices=STREAM_CHOICES, blank=True, help_text='Academic stream (for students)')

    def save(self, *args, **kwargs):
        if not self.pk and not self.is_superuser:
            self.is_active = False
        super().save(*args, **kwargs)
    
    def get_stream_display_short(self):
        """Get shortened stream name for display"""
        stream_map = {
            'common_science': 'Sci',
            'common_literature': 'Lit',
            'math': 'Math',
            'science': 'Sci',
            'languages': 'Lang',
            'literature': 'Lit',
            'management_economics': 'Mgmt',
            'civil_engineering': 'Civil',
        }
        return stream_map.get(self.stream, '')

    def __str__(self):
        return self.username
