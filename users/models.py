from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

YEAR_CHOICES = [
    (1, _('First Year')),
    (2, _('Second Year')),
    (3, _('Third Year')),
]

STREAM_CHOICES = [
    # First Year
    ('common_science', _('Common Science')),
    ('common_literature', _('Common Literature')),
    # Second & Third Year
    ('math', _('Math Stream')),
    ('science', _('Science Stream')),
    ('languages', _('Languages Stream')),
    ('literature', _('Literature Stream')),
    ('management_economics', _('Management & Economics Stream')),
    ('civil_engineering', _('Civil Engineering Stream')),
]

SUBJECT_CHOICES = [
    # Common subjects
    ('math', _('Math')),
    ('science', _('Science')),
    ('physics', _('Physics')),
    ('arabic', _('Arabic')),
    ('english', _('English')),
    ('french', _('French')),
    ('hist_geo', _('History & Geography')),
    # Stream specific
    ('civil_eng', _('Civil Engineering')),
    ('accounting', _('Accounting')),
    ('law', _('Law')),
    ('economy', _('Economy')),
    ('german', _('German')),
    ('spanish', _('Spanish')),
    ('philosophy', _('Philosophy')),
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
    
    # Field to track when the user last cleared their chat history
    last_chat_clear_time = models.DateTimeField(null=True, blank=True)

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
