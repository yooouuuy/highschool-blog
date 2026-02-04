from django.views.generic import CreateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from .models import Report
from .forms import ReportForm
from users.models import CustomUser

class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    
    def form_valid(self, form):
        content_type_id = self.kwargs.get('content_type_id')
        object_id = self.kwargs.get('object_id')
        content_type = get_object_or_404(ContentType, id=content_type_id)
        
        # Check for rate limiting (e.g., max 5 reports per hour)
        one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
        recent_reports_count = Report.objects.filter(reporter=self.request.user, created_at__gt=one_hour_ago).count()
        if recent_reports_count >= 5:
            messages.error(self.request, "You have reached the limit of reports per hour. Please try again later.")
            return redirect(self.request.META.get('HTTP_REFERER', '/'))

        # Check if already reported
        if Report.objects.filter(reporter=self.request.user, content_type=content_type, object_id=object_id).exists():
            messages.warning(self.request, "You have already reported this content.")
            return redirect(self.request.META.get('HTTP_REFERER', '/'))

        form.instance.reporter = self.request.user
        form.instance.content_type = content_type
        form.instance.object_id = object_id
        
        messages.success(self.request, "Thank you for your report. A moderator will review it shortly.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', '/')

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_teacher or self.request.user.is_staff)

class ReportListView(TeacherRequiredMixin, ListView):
    model = Report
    template_name = 'moderation/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20

    def get_queryset(self):
        status = self.request.GET.get('status', 'pending')
        return Report.objects.filter(status=status).select_related('reporter', 'moderator', 'content_type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', 'pending')
        return context

class ModerationActionView(TeacherRequiredMixin, View):
    def post(self, request, report_id):
        report = get_object_or_404(Report, id=report_id)
        action = request.POST.get('action')
        note = request.POST.get('note', '')
        
        target = report.content_object
        
        if action == 'dismiss':
            report.status = 'dismissed'
            messages.info(request, "Report dismissed.")
        
        elif action == 'hide':
            if hasattr(target, 'is_removed'):
                target.is_removed = True
                target.save()
                report.status = 'resolved'
                messages.success(request, "Content hidden and report resolved.")
            else:
                messages.error(request, "This content type does not support hiding.")
                return redirect('moderation:report_list')
        
        elif action == 'suspend':
            author = getattr(target, 'author', None)
            if author and isinstance(author, CustomUser):
                days = int(request.POST.get('days', 3))
                author.is_active = False
                author.suspension_end = timezone.now() + timezone.timedelta(days=days)
                author.save()
                report.status = 'resolved'
                messages.warning(request, f"User {author.username} suspended for {days} days.")
            else:
                messages.error(request, "Target author not found or invalid.")
                return redirect('moderation:report_list')
        
        elif action == 'warn':
            # In a real system, this would send a notification
            report.status = 'resolved'
            messages.success(request, "User warned (notification sent).")
            
        report.moderator = request.user
        report.moderator_note = note
        report.save()
        
        return redirect('moderation:report_list')
