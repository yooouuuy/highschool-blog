from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_teacher', 'is_student', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_teacher', 'is_student')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_teacher', 'is_student')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
