from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import reverse

from content.models import Lesson, Test, Resource, ForumPost, Notification

User = get_user_model()

class AdminTeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_teacher)

class DashboardView(LoginRequiredMixin, AdminTeacherRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Metrics
        context['total_students'] = User.objects.filter(is_student=True).count()
        context['total_teachers'] = User.objects.filter(is_teacher=True).count()
        context['pending_users'] = User.objects.filter(is_active=False).count()
        
        context['pending_lessons'] = Lesson.objects.filter(is_approved=False, is_removed=False).count()
        context['pending_tests'] = Test.objects.filter(is_approved=False, is_removed=False).count()
        context['pending_resources'] = Resource.objects.filter(is_approved=False, is_removed=False).count()
        context['total_pending_content'] = context['pending_lessons'] + context['pending_tests'] + context['pending_resources']

        # Recent Activity
        context['recent_users'] = User.objects.order_by('-date_joined')[:5]
        context['recent_lessons'] = Lesson.objects.filter(is_removed=False).order_by('-created_at')[:5]
        
        return context

class UserManagementView(LoginRequiredMixin, AdminTeacherRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        status = self.request.GET.get('status')
        if status == 'pending':
            queryset = queryset.filter(is_active=False)
        elif status == 'students':
            queryset = queryset.filter(is_student=True)
        elif status == 'teachers':
            queryset = queryset.filter(is_teacher=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filter'] = self.request.GET.get('status', 'all')
        return context

class ContentManagementView(LoginRequiredMixin, AdminTeacherRequiredMixin, ListView):
    template_name = 'dashboard/content_list.html'
    context_object_name = 'content_items'
    paginate_by = 20

    def get_queryset(self):
        content_type = self.request.GET.get('type', 'lesson')
        status = self.request.GET.get('status')
        
        if content_type == 'test':
            queryset = Test.objects.filter(is_removed=False).select_related('author')
        elif content_type == 'resource':
            queryset = Resource.objects.filter(is_removed=False).select_related('author')
        else:
            queryset = Lesson.objects.filter(is_removed=False).select_related('author')

        if status == 'pending':
            queryset = queryset.filter(is_approved=False)
        elif status == 'approved':
            queryset = queryset.filter(is_approved=True)
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_type'] = self.request.GET.get('type', 'lesson')
        context['current_status'] = self.request.GET.get('status', 'all')
        return context

class ActionView(LoginRequiredMixin, AdminTeacherRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        item_type = request.POST.get('item_type')
        
        try:
            if item_type == 'user':
                user = get_object_or_404(User, id=item_id)
                if action == 'approve':
                    user.is_active = True
                    user.save()
                    messages.success(request, f"User {user.username} approved.")
                elif action == 'deactivate':
                    user.is_active = False
                    user.save()
                    messages.warning(request, f"User {user.username} deactivated.")
                elif action == 'reject':
                    user.delete()
                    messages.warning(request, f"User {user.username} deleted.")
                    
            elif item_type in ['lesson', 'test', 'resource']:
                if item_type == 'lesson':
                    Model = Lesson
                elif item_type == 'test':
                    Model = Test
                elif item_type == 'resource':
                    Model = Resource
                
                item = get_object_or_404(Model, id=item_id)
                
                if action == 'approve':
                    item.is_approved = True
                    item.save()
                    messages.success(request, f"{item_type.title()} '{item}' approved.")
                    
                    # Create notification
                    Notification.objects.create(
                        recipient=item.author,
                        title=_("Content Approved"),
                        message=f"Your {item_type} '{item}' has been approved.",
                    )
                    
                elif action == 'reject':
                    item.delete()
                    messages.warning(request, f"{item_type.title()} '{item}' rejected and deleted.")
                    
                    # Create notification (if model wasn't deleted, but here we delete. 
                    # Ideally we might just mark as rejected, but for simplicity user asked for approve/reject.
                    # If deleted, we can't notify easily unless notifications are separate. 
                    # Assuming we just delete for now as per 'Reject' usually implies removal in simple systems.)

        except Exception as e:
            messages.error(request, f"Error performing action: {str(e)}")
            
        return redirect(request.META.get('HTTP_REFERER', 'dashboard:home'))
