from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from content.models import Lesson, Test, Announcement

def home(request):
    lessons = Lesson.objects.filter(is_approved=True).order_by('-created_at')[:5]
    announcements = Announcement.objects.all().order_by('-created_at')[:3]
    
    context = {
        'lessons': lessons,
        'announcements': announcements,
    }
    
    if request.user.is_authenticated and request.user.year and request.user.stream:
        context['year'] = request.user.year
        context['stream'] = request.user.stream
        from content.models import ChatMessage
        context['year_display'] = dict(ChatMessage.YEAR_CHOICES).get(request.user.year)
        context['stream_display'] = dict(ChatMessage.STREAM_CHOICES).get(request.user.stream)

    return render(request, 'main/home.html', context)

