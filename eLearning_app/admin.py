from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Teacher, Course, Material, Feedback, StatusUpdate, ChatRoom, EnrollmentNotification, MaterialNotification


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name',
         'last_name', 'email', 'profile_picture')}),
        (('eLearning App Roles'), {'fields': ('is_student', 'is_teacher')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_student', 'is_teacher')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Material)
admin.site.register(Feedback)
admin.site.register(StatusUpdate)
admin.site.register(ChatRoom)
admin.site.register(EnrollmentNotification)
admin.site.register(MaterialNotification)
