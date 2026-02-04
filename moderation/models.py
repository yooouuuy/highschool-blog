from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

class Report(models.Model):
    REASON_CHOICES = [
        ('spam', _('Spam')),
        ('abuse', _('Abuse/Harassment')),
        ('off_topic', _('Off-topic')),
        ('other', _('Other')),
    ]
    STATUS_CHOICES = [
        ('pending', _('Pending Review')),
        ('resolved', _('Resolved (Actions Taken)')),
        ('dismissed', _('Dismissed (No Action)')),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reports_sent'
    )
    
    # Generic relationship to target content
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True, verbose_name=_('Additional description'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reports_handled'
    )
    moderator_note = models.TextField(blank=True, verbose_name=_('Moderator notes'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        # Prevent same user reporting same content twice
        unique_together = ('reporter', 'content_type', 'object_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"Report by {self.reporter} on {self.content_object}"
