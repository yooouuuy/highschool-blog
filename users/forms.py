from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'real_name', 'nickname', 'bio', 'profile_pic', 'is_teacher', 'is_student', 'year', 'stream')
        help_texts = {
            'real_name': _('Your full real name (cannot be changed later).'),
            'nickname': _('A display name you can change.'),
            'profile_pic': _('Optional profile picture.'),
            'year': _('Select your year level (for students only).'),
            'stream': _('Your academic stream (1st: Common Sci/Lit, 2nd/3rd: specialized streams).'),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('nickname', 'bio', 'profile_pic')
        help_texts = {
            'nickname': _('This name will be displayed to others.'),
            'bio': _('Tell us a bit about yourself.'),
        }
