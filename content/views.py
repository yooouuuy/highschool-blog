from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _

from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Lesson, Test, Question, Result, Announcement, ChatMessage, Resource, ForumThread, ForumPost, LessonComment, StudentAnswer, Notification
from .forms import LessonForm, TestForm, QuestionForm, AnnouncementForm, ResourceForm, ForumThreadForm, ForumPostForm, LessonCommentForm
from django.contrib.contenttypes.models import ContentType
from users.models import YEAR_CHOICES, STREAM_CHOICES, SUBJECT_CHOICES

def is_teacher(user):
    return user.is_authenticated and user.is_active and (user.is_teacher or user.is_staff)

from django.db.models import Q, Count

# ... (imports)

class LessonListView(ListView):
    model = Lesson
    template_name = 'content/lesson_list.html'
    context_object_name = 'lessons'
    paginate_by = 10

    def get_queryset(self):
        queryset = Lesson.objects.select_related('author').filter(is_approved=True, is_removed=False).order_by('-created_at')
        year = self.request.GET.get('year')
        stream = self.request.GET.get('stream')
        subject = self.request.GET.get('subject')
        
        if year:
            queryset = queryset.filter(year=year)
        if stream:
            queryset = queryset.filter(stream=stream)
        if subject:
            queryset = queryset.filter(subject=subject)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['announcements'] = Announcement.objects.filter(is_removed=False).order_by('-created_at')[:2]
        context['year_choices'] = YEAR_CHOICES
        context['stream_choices'] = STREAM_CHOICES
        context['subject_choices'] = SUBJECT_CHOICES
        context['filters'] = {
            'year': self.request.GET.get('year'),
            'stream': self.request.GET.get('stream'),
            'subject': self.request.GET.get('subject')
        }
        context['total_count'] = self.get_queryset().count()
        return context

class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'content/lesson_detail.html'
    context_object_name = 'lesson'

    def get_queryset(self):
        return Lesson.objects.filter(is_removed=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(is_removed=False)
        context['comment_form'] = LessonCommentForm()
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = LessonCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.lesson = self.object
            comment.author = request.user
            comment.save()
            messages.success(request, _('Comment added successfully.'))

            return redirect('lesson_detail', pk=self.object.pk)
        return self.render_to_response(self.get_context_data(comment_form=form))

class LessonCreateView(LoginRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'content/lesson_form.html'
    success_url = reverse_lazy('lesson_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        if self.request.user.is_teacher or self.request.user.is_staff:
            form.instance.is_approved = True
            messages.success(self.request, _('Lesson published successfully.'))
        else:
            form.instance.is_approved = False
            messages.success(self.request, _('Your lesson has been submitted for approval.'))

        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        # Pre-fill from GET params or user profile
        initial['year'] = self.request.GET.get('year') or getattr(self.request.user, 'year', None)
        initial['stream'] = self.request.GET.get('stream') or getattr(self.request.user, 'stream', None)
        initial['subject'] = self.request.GET.get('subject')
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject_choices'] = SUBJECT_CHOICES
        context['stream_choices'] = STREAM_CHOICES
        context['year_choices'] = YEAR_CHOICES
        return context

@login_required
def test_create(request):
    if request.method == 'POST':
        form = TestForm(request.POST, request.FILES)
        if form.is_valid():
            test = form.save(commit=False)
            test.author = request.user
            if request.user.is_teacher or request.user.is_staff:
                test.is_approved = True
                test.save()
                messages.success(request, _('Test published successfully.'))

                return redirect('test_detail', pk=test.pk)
            else:
                test.is_approved = False
                test.save()
                messages.success(request, _('Your test has been submitted for approval.'))

                return redirect('test_list')
    else:
        initial = {
            'year': request.GET.get('year') or getattr(request.user, 'year', None),
            'stream': request.GET.get('stream') or getattr(request.user, 'stream', None),
            'subject': request.GET.get('subject')
        }
        form = TestForm(initial=initial)
    
    return render(request, 'content/test_form.html', {
        'form': form,
        'subject_choices': SUBJECT_CHOICES,
        'stream_choices': STREAM_CHOICES,
        'year_choices': YEAR_CHOICES
    })

@login_required
def test_detail(request, pk):
    test = get_object_or_404(Test, pk=pk, is_removed=False)
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
    test = get_object_or_404(Test, pk=pk, is_removed=False)
    questions = test.questions.filter(is_removed=False)
    
    if not questions.exists():
        messages.warning(request, _("This test does not have any questions yet."))

        return redirect('test_detail', pk=test.pk)
    
    if request.method == 'POST':
        score = 0
        all_answered = True
        answers = {}
        
        for question in questions:
            selected_option = request.POST.get(f'question_{question.id}')
            if not selected_option:
                all_answered = False
            answers[question.id] = selected_option
            
            if selected_option == question.correct_option:
                score += 1
        
        if not all_answered:
            messages.error(request, _('Please answer all questions before submitting.'))

            return render(request, 'content/take_test.html', {
                'test': test, 
                'questions': questions,
                'previous_answers': answers
            })

        result = Result.objects.create(
            student=request.user,
            test=test,
            score=score,
            total_questions=questions.count()
        )

        # Save individual answers
        for q_id, selected_opt in answers.items():
            question = questions.get(id=q_id)
            StudentAnswer.objects.create(
                result=result,
                question=question,
                selected_option=selected_opt,
                is_correct=(selected_opt == question.correct_option)
            )

        messages.success(request, _('Test completed! Your score: {score}/{total}').format(score=score, total=questions.count()))

        return redirect('result_detail', pk=result.pk)
    
    return render(request, 'content/take_test.html', {'test': test, 'questions': questions})

@login_required
def result_detail(request, pk):
    result = get_object_or_404(Result, pk=pk)
    # Check if the test itself was removed
    if result.test.is_removed:
        return redirect('test_list')
    if request.user != result.student:
        return redirect('lesson_list')
    return render(request, 'content/result_detail.html', {'result': result})

def test_list(request):
    tests = Test.objects.select_related('author').filter(is_approved=True, is_removed=False).order_by('-created_at')
    
    year = request.GET.get('year')
    stream = request.GET.get('stream')
    subject = request.GET.get('subject')
    
    if year:
        tests = tests.filter(year=year)
    if stream:
        tests = tests.filter(stream=stream)
    if subject:
        tests = tests.filter(subject=subject)
        
    return render(request, 'content/test_list.html', {
        'tests': tests,
        'year_choices': YEAR_CHOICES,
        'stream_choices': STREAM_CHOICES,
        'subject_choices': SUBJECT_CHOICES,
        'filters': {'year': year, 'stream': stream, 'subject': subject},
        'total_count': tests.count()
    })

@login_required
def student_dashboard(request):
    results = Result.objects.filter(student=request.user).order_by('-date_taken')
    pending_lessons = Lesson.objects.filter(author=request.user, is_approved=False, is_removed=False).order_by('-created_at')
    pending_tests = Test.objects.filter(author=request.user, is_approved=False, is_removed=False).order_by('-created_at')
    pending_resources = Resource.objects.filter(author=request.user, is_approved=False, is_removed=False).order_by('-created_at')
    
    return render(request, 'content/student_dashboard.html', {
        'results': results,
        'pending_lessons': pending_lessons,
        'pending_tests': pending_tests,
        'pending_resources': pending_resources
    })


@login_required
@user_passes_test(is_teacher)
def pending_lessons(request):
    lessons = Lesson.objects.filter(is_approved=False, is_removed=False).order_by('-created_at')
    tests = Test.objects.filter(is_approved=False, is_removed=False).order_by('-created_at')
    resources = Resource.objects.filter(is_approved=False, is_removed=False).order_by('-created_at')
    return render(request, 'content/pending_lessons.html', {
        'lessons': lessons, 
        'tests': tests,
        'resources': resources
    })

@login_required
@user_passes_test(is_teacher)
def approve_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk, is_removed=False)
    lesson.is_approved = True
    lesson.save()
    return redirect('pending_lessons')

@login_required
@user_passes_test(is_teacher)
def approve_test(request, pk):
    test = get_object_or_404(Test, pk=pk, is_removed=False)
    test.is_approved = True
    test.save()
    return redirect('pending_lessons')

@login_required
@user_passes_test(is_teacher)
def approve_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk, is_removed=False)
    resource.is_approved = True
    resource.save()
    messages.success(request, _('Resource "{title}" approved.').format(title=resource.title))

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
    announcement = get_object_or_404(Announcement, pk=pk, is_removed=False)
    if request.user.is_staff or request.user == announcement.author:
        announcement.is_removed = True
        announcement.save()
    return redirect('home')

@login_required
def clear_chat_history(request):
    if request.method == 'POST':
        request.user.last_chat_clear_time = timezone.now()
        request.user.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
def chat_room(request, year, stream):
    if not (request.user.is_teacher or request.user.is_staff or 
            (request.user.year == year and request.user.stream == stream)):
        return redirect('home')
    
    chat_messages = ChatMessage.objects.filter(year=year, stream=stream, is_removed=False)
    if request.user.last_chat_clear_time:
        chat_messages = chat_messages.filter(created_at__gt=request.user.last_chat_clear_time)
        
    chat_messages = chat_messages.order_by('-created_at')[:50]
    chat_messages = reversed(chat_messages)
    
    stream_display = dict(STREAM_CHOICES).get(stream, stream)
    
    return render(request, 'content/chat.html', {
        'year': year,
        'stream': stream,
        'year_display': dict(YEAR_CHOICES).get(year, year),
        'stream_display': stream_display,
        'chat_content_type_id': ContentType.objects.get_for_model(ChatMessage).id
    })

@login_required
def send_message(request, year, stream):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not (request.user.is_teacher or request.user.is_staff or 
                (request.user.year == year and request.user.stream == stream)):
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        
        message_text = request.POST.get('message', '').strip()
        if message_text:
            msg = ChatMessage.objects.create(
                author=request.user,
                year=year,
                stream=stream,
                message=message_text
            )
            return JsonResponse({
                'success': True,
                'message': {
                    'id': msg.id,
                    'author': msg.author.nickname or msg.author.real_name or msg.author.username,
                    'is_mine': True,
                    'text': msg.message,
                    'time': msg.created_at.strftime('%b %d, %H:%M')
                }
            })
    
    return JsonResponse({'success': False}, status=400)

@login_required
def get_messages(request, year, stream):
    if not (request.user.is_teacher or request.user.is_staff or 
            (request.user.year == year and request.user.stream == stream)):
        return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
    
    last_id = request.GET.get('last_id')
    messages_query = ChatMessage.objects.filter(year=year, stream=stream, is_removed=False)
    
    if request.user.last_chat_clear_time:
        messages_query = messages_query.filter(created_at__gt=request.user.last_chat_clear_time)
    
    if last_id and last_id.isdigit():
        messages_query = messages_query.filter(id__gt=int(last_id))
    else:
        # Load only the last 50 messages locally to prevent huge payload
        messages_query = messages_query.order_by('-created_at')[:50]
        # Reverse back to chronological order for display
        messages_query = sorted(messages_query, key=lambda x: x.created_at)

    message_list = []
    for msg in messages_query:
        message_list.append({
            'id': msg.id,
            'author': msg.author.nickname or msg.author.real_name or msg.author.username,
            'is_mine': msg.author == request.user,
            'text': msg.message,
            'time': msg.created_at.strftime('%b %d, %H:%M')
        })
    
    return JsonResponse({'success': True, 'messages': message_list})

@login_required
def edit_chat_message(request, pk):
    if request.method == 'POST':
        message = get_object_or_404(ChatMessage, pk=pk)
        if message.author != request.user:
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        
        new_text = request.POST.get('message', '').strip()
        if not new_text:
            return JsonResponse({'success': False, 'error': 'Message cannot be empty'}, status=400)
        
        message.message = new_text
        message.save()
        return JsonResponse({'success': True, 'text': message.message})
    return JsonResponse({'success': False}, status=400)

@login_required
def delete_chat_message(request, pk):
    if request.method == 'POST':
        message = get_object_or_404(ChatMessage, pk=pk)
        if message.author == request.user or request.user.is_staff or request.user.is_teacher:
            message.is_removed = True
            message.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
    return JsonResponse({'success': False}, status=400)

# Library Views
def resource_list(request):
    resources = Resource.objects.select_related('author').filter(is_approved=True, is_removed=False).order_by('-created_at')
    
    year = request.GET.get('year')
    stream = request.GET.get('stream')
    subject = request.GET.get('subject')
    res_type = request.GET.get('type')
    
    if year:
        resources = resources.filter(year=year)
    if stream:
        resources = resources.filter(stream=stream)
    if subject:
        resources = resources.filter(subject=subject)
    if res_type:
        resources = resources.filter(type=res_type)
        
    return render(request, 'content/library.html', {
        'resources': resources,
        'year_choices': YEAR_CHOICES,
        'stream_choices': STREAM_CHOICES,
        'subject_choices': SUBJECT_CHOICES,
        'type_choices': Resource.RESOURCE_TYPES,
        'filters': {'year': year, 'stream': stream, 'subject': subject, 'type': res_type},
        'total_count': resources.count()
    })

@login_required
def resource_create(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.author = request.user
            if request.user.is_teacher or request.user.is_staff:
                resource.is_approved = True
                messages.success(request, _('Resource uploaded successfully.'))
            else:
                resource.is_approved = False
                messages.success(request, _('Resource submitted for approval.'))

            resource.save()
            return redirect('resource_list')
    else:
        form = ResourceForm()
    return render(request, 'content/resource_form.html', {
        'form': form,
        'year_choices': YEAR_CHOICES,
        'stream_choices': STREAM_CHOICES,
        'subject_choices': SUBJECT_CHOICES
    })

# Forum Views
@login_required
def forum_subjects(request):
    return render(request, 'content/forum_subjects.html', {
        'subjects': SUBJECT_CHOICES
    })

@login_required
def forum_thread_list(request, subject):
    threads = ForumThread.objects.select_related('author').filter(subject=subject, is_removed=False).annotate(posts_count=Count('posts'))
    category = request.GET.get('category')
    
    year = request.GET.get('year')
    stream = request.GET.get('stream')
    
    if category:
        threads = threads.filter(category=category)
    if year:
        threads = threads.filter(year=year)
    if stream:
        threads = threads.filter(stream=stream)
        
    subject_display = dict(SUBJECT_CHOICES).get(subject, subject)
    return render(request, 'content/forum_thread_list.html', {
        'threads': threads,
        'subject': subject,
        'subject_display': subject_display,
        'current_category': category,
        'year_choices': YEAR_CHOICES,
        'stream_choices': STREAM_CHOICES,
        'current_year': year,
        'current_stream': stream
    })

@login_required
def forum_thread_create(request, subject):
    if request.method == 'POST':
        form = ForumThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user
            thread.subject = subject
            thread.save()
            
            # Create the first post
            ForumPost.objects.create(
                thread=thread,
                author=request.user,
                content=request.POST.get('content')
            )
            return redirect('forum_thread_detail', pk=thread.pk)
    else:
        initial = {
            'subject': subject,
            'year': request.GET.get('year') or getattr(request.user, 'year', None),
            'stream': request.GET.get('stream') or getattr(request.user, 'stream', None)
        }
        form = ForumThreadForm(initial=initial)
    return render(request, 'content/forum_thread_form.html', {
        'form': form,
        'subject': subject,
        'year_choices': YEAR_CHOICES,
        'stream_choices': STREAM_CHOICES,
        'subject_choices': SUBJECT_CHOICES
    })

@login_required
def forum_thread_detail(request, pk):
    thread = get_object_or_404(ForumThread, pk=pk, is_removed=False)
    posts = thread.posts.filter(is_removed=False)
    
    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.thread = thread
            post.author = request.user
            post.save()
            return redirect('forum_thread_detail', pk=thread.pk)
    else:
        form = ForumPostForm()
        
    return render(request, 'content/forum_thread_detail.html', {
        'thread': thread,
        'posts': posts,
        'form': form
    })

# Feedback View
@login_required
@user_passes_test(is_teacher)
def add_feedback(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.user != result.test.author:
        messages.error(request, _("You can only leave feedback for tests you created."))

        return redirect('result_detail', pk=result.pk)
        
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')
        if feedback_text:
            result.teacher_feedback = feedback_text
            result.feedback_date = timezone.now()
            result.save()
            messages.success(request, _("Feedback added successfully."))

    
    return redirect('result_detail', pk=result.pk)

# Deletion Views
@login_required
def delete_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.user.is_staff or request.user == lesson.author:
        lesson.is_removed = True
        lesson.save()
        messages.success(request, _("Lesson deleted successfully."))
    return redirect('lesson_list')

@login_required
def delete_test(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.user.is_staff or request.user == test.author:
        test.is_removed = True
        test.save()
        messages.success(request, _("Test deleted successfully."))

    return redirect('test_list')

@login_required
def delete_forum_thread(request, pk):
    thread = get_object_or_404(ForumThread, pk=pk)
    subject = thread.subject
    if request.user.is_staff or request.user == thread.author:
        thread.is_removed = True
        thread.save()
        messages.success(request, _("Discussion thread deleted successfully."))

    return redirect('forum_thread_list', subject=subject)

@login_required
def delete_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.user.is_staff or request.user == resource.author:
        resource.is_removed = True
        resource.save()
        messages.success(request, _("Resource deleted successfully."))

    return redirect('resource_list')

def search_view(request):
    query = request.GET.get('q', '')
    lessons = []
    tests = []
    resources = []
    
    if query:
        lessons = Lesson.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            is_approved=True, is_removed=False
        ).distinct()
        
        tests = Test.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            is_approved=True, is_removed=False
        ).distinct()
        
        resources = Resource.objects.filter(
            Q(title__icontains=query),
            is_approved=True, is_removed=False
        ).distinct()
        
    return render(request, 'content/search_results.html', {
        'query': query,
        'lessons': lessons,
        'tests': tests,
        'resources': resources
    })

@login_required
@user_passes_test(is_teacher)
def test_analytics(request, pk):
    test = get_object_or_404(Test, pk=pk, is_removed=False)
    if request.user != test.author and not request.user.is_staff:
        return redirect('test_detail', pk=pk)
        
    results = Result.objects.filter(test=test)
    total_students = results.count()
    
    if total_students == 0:
        return render(request, 'content/test_analytics.html', {
            'test': test,
            'total_students': 0
        })
        
    # Calculate stats
    avg_score = sum(r.score for r in results) / total_students
    max_score = max(r.score for r in results)
    min_score = min(r.score for r in results)
    
    # Question analysis
    questions = test.questions.filter(is_removed=False)
    question_stats = []
    
    for q in questions:
        answers = StudentAnswer.objects.filter(question=q)
        correct_count = answers.filter(is_correct=True).count()
        total_answers = answers.count()
        percentage = (correct_count / total_answers * 100) if total_answers > 0 else 0
        
        question_stats.append({
            'question': q,
            'correct_percentage': round(percentage, 1),
            'wrong_count': total_answers - correct_count,
            'total_attempts': total_answers
        })
        
    # Sort by difficulty (lowest percentage first)
    question_stats.sort(key=lambda x: x['correct_percentage'])
    
    return render(request, 'content/test_analytics.html', {
        'test': test,
        'total_students': total_students,
        'avg_score': round(avg_score, 1),
        'max_score': max_score,
        'min_score': min_score,
        'question_stats': question_stats
    })

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user, is_removed=False)
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'content/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user, is_removed=False)
    notification.is_read = True
    notification.save()
    
    if notification.link:
        return redirect(notification.link)
    return redirect('notification_list')
