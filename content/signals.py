from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Lesson, Test, Resource, Announcement, Notification
from django.contrib.auth import get_user_model

@receiver(post_save, sender=Lesson)
def notify_lesson_approval(sender, instance, created, **kwargs):
    if not created and instance.is_approved:
        # Check if it was just approved (naive check, assuming if it's approved and not created, it's an approval action)
        # Ideally we'd check against previous state, but this is a simple implementation
        Notification.objects.create(
            recipient=instance.author,
            title="Lesson Approved",
            message=f"Your lesson '{instance.title}' has been approved and is now live.",
            link=f"/content/lessons/{instance.pk}/"
        )

@receiver(post_save, sender=Test)
def notify_test_approval(sender, instance, created, **kwargs):
    if not created and instance.is_approved:
        Notification.objects.create(
            recipient=instance.author,
            title="Test Approved",
            message=f"Your test '{instance.title}' has been approved and is now live.",
            link=f"/content/tests/{instance.pk}/"
        )

@receiver(post_save, sender=Resource)
def notify_resource_approval(sender, instance, created, **kwargs):
    if not created and instance.is_approved:
        Notification.objects.create(
            recipient=instance.author,
            title="Resource Approved",
            message=f"Your resource '{instance.title}' has been approved.",
            link="/content/library/"
        )

@receiver(post_save, sender=Announcement)
def notify_announcement(sender, instance, created, **kwargs):
    if created:
        User = get_user_model()
        # Notify all active users (students AND teachers)
        recipients = User.objects.filter(is_active=True)
        notifications = []
        for user in recipients:
            notifications.append(Notification(
                recipient=user,
                announcement=instance,
                title="New Announcement",
                message=f"New announcement: {instance.title}",
                link="/"
            ))
        Notification.objects.bulk_create(notifications)

@receiver(post_save, sender=Lesson)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Lesson.objects.get(pk=instance.pk).pdf_file
    except Lesson.DoesNotExist:
        return False

    new_file = instance.pdf_file
    if not old_file == new_file:
        if old_file:
            old_file.delete(save=False)

@receiver(post_delete, sender=Lesson)
def auto_delete_file_on_delete_lesson(sender, instance, **kwargs):
    """
    Deletes file from filesystem when corresponding `Lesson` object is deleted.
    """
    if instance.pdf_file:
        instance.pdf_file.delete(save=False)

@receiver(post_delete, sender=Test)
def auto_delete_file_on_delete_test(sender, instance, **kwargs):
    if instance.pdf_file:
        instance.pdf_file.delete(save=False)

@receiver(post_delete, sender=Resource)
def auto_delete_file_on_delete_resource(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)
