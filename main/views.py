from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from content.models import Lesson, Test, Announcement

def home(request):
    lessons = Lesson.objects.filter(is_approved=True, is_removed=False).order_by('-created_at')[:5]
    tests = Test.objects.filter(is_approved=True, is_removed=False).order_by('-created_at')[:5]
    announcements = Announcement.objects.filter(is_removed=False).order_by('-created_at')[:3]
    
    context = {
        'lessons': lessons,
        'tests': tests,
        'announcements': announcements,
    }
    
    if request.user.is_authenticated:
        # Pass year and stream for student chat, even if they haven't set them yet (to show a friendly message)
        context['year'] = request.user.year
        context['stream'] = request.user.stream
        
        from users.models import YEAR_CHOICES, STREAM_CHOICES
        if request.user.year:
            context['year_display'] = dict(YEAR_CHOICES).get(request.user.year)
        if request.user.stream:
            context['stream_display'] = dict(STREAM_CHOICES).get(request.user.stream)

    return render(request, 'main/home.html', context)

