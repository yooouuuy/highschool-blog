from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'real_name', 'nickname', 'bio', 'profile_pic', 'is_teacher', 'is_student', 'year', 'stream')
        help_texts = {
            'real_name': 'Your full real name (cannot be changed later).',
            'nickname': 'A display name you can change.',
            'profile_pic': 'Optional profile picture.',
            'year': 'Select your year level (for students only).',
            'stream': 'Your academic stream (1st: Common Sci/Lit, 2nd/3rd: specialized streams).',
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('nickname', 'bio', 'profile_pic')
        help_texts = {
            'nickname': 'This name will be displayed to others.',
            'bio': 'Tell us a bit about yourself.',
        }
