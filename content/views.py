from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Lesson, Test, Question, Result, Announcement, ChatMessage
from .forms import LessonForm, TestForm, QuestionForm, AnnouncementForm
from users.models import YEAR_CHOICES, STREAM_CHOICES, SUBJECT_CHOICES

def is_teacher(user):
    return user.is_authenticated and (user.is_teacher or user.is_staff)

def lesson_list(request):
    lessons = Lesson.objects.filter(is_approved=True).order_by('-created_at')
    
    year = request.GET.get('year')
    stream = request.GET.get('stream')
    subject = request.GET.get('subject')
    
    if year:
        lessons = lessons.filter(year=year)
    if stream:
        lessons = lessons.filter(stream=stream)
    if subject:
        lessons = lessons.filter(subject=subject)
        
    announcements = Announcement.objects.all().order_by('-created_at')[:2]
    
    from users.models import YEAR_CHOICES, STREAM_CHOICES, SUBJECT_CHOICES
    
    return render(request, 'content/lesson_list.html', {
        'lessons': lessons, 
        'announcements': announcements,
        'year_choices': YEAR_CHOICES,
        'stream_choices': STREAM_CHOICES,
        'subject_choices': SUBJECT_CHOICES,
        'filters': {'year': year, 'stream': stream, 'subject': subject}
    })

@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    return render(request, 'content/lesson_detail.html', {'lesson': lesson})

@login_required
def lesson_create(request):
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.author = request.user
            # Auto-approve for teachers/staff, otherwise pending
            if request.user.is_teacher or request.user.is_staff:
                lesson.is_approved = True
            else:
                lesson.is_approved = False
            lesson.save()
            return redirect('lesson_list')
    else:
        form = LessonForm()
    
    from users.models import SUBJECT_CHOICES, STREAM_CHOICES
    return render(request, 'content/lesson_form.html', {
        'form': form,
        'subject_choices': SUBJECT_CHOICES,
        'stream_choices': STREAM_CHOICES
    })

@login_required
def test_create(request):
    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.author = request.user
            test.save()
            return redirect('test_detail', pk=test.pk)
    else:
        form = TestForm()
    
    from users.models import SUBJECT_CHOICES, STREAM_CHOICES
    return render(request, 'content/test_form.html', {
        'form': form,
        'subject_choices': SUBJECT_CHOICES,
        'stream_choices': STREAM_CHOICES
    })

@login_required
def test_detail(request, pk):
    test = get_object_or_404(Test, pk=pk)
    return render(request, 'content/test_detail.html', {'test': test})

@user_passes_test(is_teacher)
def question_add(request, test_pk):
    test = get_object_or_404(Test, pk=test_pk)
    if request.user != test.author:
        return redirect('test_detail', pk=test.pk)
        
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.test = test
            question.save()
            return redirect('test_detail', pk=test.pk)
    else:
        form = QuestionForm()
    return render(request, 'content/question_form.html', {'form': form, 'test': test})

@login_required
def take_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    questions = test.questions.all()
    
    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_option = request.POST.get(f'question_{question.id}')
            if selected_option == question.correct_option:
                score += 1
        
        result = Result.objects.create(
            student=request.user,
            test=test,
            score=score,
            total_questions=questions.count()
        )
        return redirect('result_detail', pk=result.pk)
    
    return render(request, 'content/take_test.html', {'test': test, 'questions': questions})

@login_required
def result_detail(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.user != result.student:
        return redirect('lesson_list') # Or some error page
    return render(request, 'content/result_detail.html', {'result': result})

def test_list(request):
    tests = Test.objects.all().order_by('-created_at')
    
    year = request.GET.get('year')
    stream = request.GET.get('stream')
    subject = request.GET.get('subject')
    
    if year:
        tests = tests.filter(year=year)
    if stream:
        tests = tests.filter(stream=stream)
    if subject:
        tests = tests.filter(subject=subject)
        
    from users.models import YEAR_CHOICES, STREAM_CHOICES, SUBJECT_CHOICES
    
    return render(request, 'content/test_list.html', {
        'tests': tests,
        'year_choices': YEAR_CHOICES,
        'stream_choices': STREAM_CHOICES,
        'subject_choices': SUBJECT_CHOICES,
        'filters': {'year': year, 'stream': stream, 'subject': subject}
    })

@login_required
def student_dashboard(request):
    results = Result.objects.filter(student=request.user).order_by('-date_taken')
    return render(request, 'content/student_dashboard.html', {'results': results})

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    # Get results for tests created by this teacher
    results = Result.objects.filter(test__author=request.user).order_by('-date_taken')
    return render(request, 'content/teacher_dashboard.html', {'results': results})

@login_required
@user_passes_test(is_teacher)
def pending_lessons(request):
    lessons = Lesson.objects.filter(is_approved=False).order_by('-created_at')
    return render(request, 'content/pending_lessons.html', {'lessons': lessons})

@login_required
@user_passes_test(is_teacher)
def approve_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    lesson.is_approved = True
    lesson.save()
    return redirect('pending_lessons')

@login_required
@user_passes_test(is_teacher)
def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            announcement.save()
            return redirect('home')
    else:
        form = AnnouncementForm()
    return render(request, 'content/announcement_form.html', {'form': form})

@login_required
def delete_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    # Only author or staff can delete
    if request.user.is_staff or request.user == announcement.author:
        announcement.delete()
    return redirect('home')

@login_required
def chat_room(request, year, stream):
    # Allow teachers/staff to access all chats, students only their year-stream
    if not (request.user.is_teacher or request.user.is_staff or 
            (request.user.year == year and request.user.stream == stream)):
        return redirect('home')
    
    messages = ChatMessage.objects.filter(year=year, stream=stream).order_by('-created_at')[:50]
    messages = reversed(messages)  # Show oldest first
    
    stream_display = dict(ChatMessage.STREAM_CHOICES).get(stream, stream)
    
    return render(request, 'content/chat.html', {
        'year': year,
        'stream': stream,
        'messages': messages,
        'year_display': dict(ChatMessage.YEAR_CHOICES)[year],
        'stream_display': stream_display
    })

@login_required
def send_message(request, year, stream):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Allow teachers/staff to send to any chat, students only their year-stream
        if not (request.user.is_teacher or request.user.is_staff or 
                (request.user.year == year and request.user.stream == stream)):
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        
        message_text = request.POST.get('message', '').strip()
        if message_text:
            msg = ChatMessage.objects.create(
                author=request.user,
                year=year,
                stream=stream,
                message=message_text
            )
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'message': {
                    'id': msg.id,
                    'author': msg.author.nickname or msg.author.real_name or msg.author.username,
                    'is_mine': True,
                    'text': msg.message,
                    'time': msg.created_at.strftime('%H:%M')
                }
            })
    
    from django.http import JsonResponse
    return JsonResponse({'success': False}, status=400)

@login_required
def get_messages(request, year, stream):
    if not (request.user.is_teacher or request.user.is_staff or 
            (request.user.year == year and request.user.stream == stream)):
        from django.http import JsonResponse
        return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
    
    last_id = request.GET.get('last_id')
    messages_query = ChatMessage.objects.filter(year=year, stream=stream)
    
    if last_id:
        messages_query = messages_query.filter(id__gt=last_id)
    else:
        messages_query = messages_query.order_by('-created_at')[:50]
        messages_query = sorted(messages_query, key=lambda x: x.created_at)

    message_list = []
    for msg in messages_query:
        message_list.append({
            'id': msg.id,
            'author': msg.author.nickname or msg.author.real_name or msg.author.username,
            'is_mine': msg.author == request.user,
            'text': msg.message,
            'time': msg.created_at.strftime('%H:%M')
        })
    
    from django.http import JsonResponse
    return JsonResponse({'success': True, 'messages': message_list})
