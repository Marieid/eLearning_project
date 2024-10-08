from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Course, Material, Feedback, StatusUpdate, ChatRoom, Enrollment, EnrollmentNotification, MaterialNotification, elearnUser, BlockNotification


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name',
         'last_name', 'email', 'profile_picture')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'email', 'first_name',
                    'last_name', 'is_staff', 'get_groups')

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'


admin.site.register(User, CustomUserAdmin)

admin.site.register(Course)
admin.site.register(Material)
admin.site.register(Feedback)
admin.site.register(StatusUpdate)
admin.site.register(ChatRoom)
admin.site.register(Enrollment)
admin.site.register(EnrollmentNotification)
admin.site.register(MaterialNotification)
admin.site.register(elearnUser)
admin.site.register(BlockNotification)
