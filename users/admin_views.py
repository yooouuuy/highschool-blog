from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model

User = get_user_model()

def is_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_teacher)

@login_required
@user_passes_test(is_staff)
def pending_users(request):
    users = User.objects.filter(is_active=False).order_by('-date_joined')
    return render(request, 'users/pending_users.html', {'users': users})

@login_required
@user_passes_test(is_staff)
def approve_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = True
    user.save()
    return redirect('pending_users')
