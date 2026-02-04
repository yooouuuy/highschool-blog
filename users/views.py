from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from content.models import Lesson, Test, Resource
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import CustomUserCreationForm, UserUpdateForm
from .models import YEAR_CHOICES, STREAM_CHOICES

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Do not login. Redirect to pending approval page.
            return redirect('registration_pending')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {
        'form': form,
        'year_choices': YEAR_CHOICES,
        'stream_choices': STREAM_CHOICES
    })

def registration_pending(request):
    return render(request, 'users/registration_pending.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {
        'form': form,
        'year_choices': YEAR_CHOICES,
        'stream_choices': STREAM_CHOICES
    })

def teacher_profile(request, username):
    User = get_user_model()
    profile_user = get_object_or_404(User, username=username)
    
    lessons = Lesson.objects.filter(author=profile_user, is_approved=True).order_by('-created_at')
    tests = Test.objects.filter(author=profile_user, is_approved=True).order_by('-created_at')
    resources = Resource.objects.filter(author=profile_user, is_approved=True).order_by('-created_at')
    
    return render(request, 'users/teacher_profile.html', {
        'profile_user': profile_user,
        'lessons': lessons,
        'tests': tests,
        'resources': resources
    })
