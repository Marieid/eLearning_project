from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission
from .models import User, Course, Teacher, Student


class StudentRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('first_name', 'last_name', 'email',
             'profile_picture')

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Check file type (for allowed image types)
            if not profile_picture.content_type.startswith('image/'):
                raise forms.ValidationError(
                    "Please upload a valid image file.")

            # Check file size (limit can be adjusted as needed)
            if profile_picture.size > 1024 * 1024:  # 1MB limit
                raise forms.ValidationError(
                    "Image file too large (maximum 1MB).")

        return profile_picture

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        if commit:
            user.save()
            Student.objects.create(user=user)
            view_user_permission = Permission.objects.filter(
                codename='view_user').first()
            if view_user_permission:
                user.user_permissions.add(view_user_permission)
        return user


class TeacherRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('first_name', 'last_name', 'email', 'profile_picture')

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Check file type (for allowed image types)
            if not profile_picture.content_type.startswith('image/'):
                raise forms.ValidationError(
                    "Please upload a valid image file.")

            # Check file size (limit can be adjusted as needed)
            if profile_picture.size > 1024 * 1024:  # 1MB limit
                raise forms.ValidationError(
                    "Image file too large (maximum 1MB).")

        return profile_picture

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
            Teacher.objects.create(user=user)
            view_user_permission = Permission.objects.filter(
                codename='view_user').first()
            if view_user_permission:
                user.user_permissions.add(view_user_permission)
        return user


class CourseCreationForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'description', 'start_date', 'end_date']
        # You can customize field widgets or add validation here if needed
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'placeholder': 'yyyy-mm-dd'}))
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'placeholder': 'yyyy-mm-dd'}))
    enrollment_status = forms.ChoiceField(
        choices=Course._meta.get_field('enrollment_status').choices)