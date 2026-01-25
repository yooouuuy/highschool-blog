from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import CustomUser

@receiver(post_delete, sender=CustomUser)
def auto_delete_profile_pic_on_delete(sender, instance, **kwargs):
    if instance.profile_pic:
        instance.profile_pic.delete(save=False)

@receiver(post_save, sender=CustomUser)
def auto_delete_profile_pic_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = CustomUser.objects.get(pk=instance.pk).profile_pic
    except CustomUser.DoesNotExist:
        return False

    new_file = instance.profile_pic
    if not old_file == new_file:
        if old_file:
            old_file.delete(save=False)
