from .models import Feedback
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission
from .models import User, Course, elearnUser, Material, Feedback, StatusUpdate, ChatRoom


class StudentRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('first_name', 'last_name', 'email',
             'profile_picture')

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Checks file extension (for allowed image types)
            if not profile_picture.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise forms.ValidationError(
                    "Please upload a valid image file.")

            if profile_picture.size > 2.5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Image file too large (maximum 1MB).")

        return profile_picture

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            elearnUser.objects.create(user=user, user_type='student')
            # Adds the user to the 'students' group
            students_group = Group.objects.get(name='Students')
            user.groups.add(students_group)
        return user


class TeacherRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('first_name', 'last_name', 'email', 'profile_picture')

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Checks file extension (for allowed image types)
            if not profile_picture.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise forms.ValidationError(
                    "Please upload a valid image file.")

            # Checks file size (limit can be adjusted as needed)
            if profile_picture.size > 2.5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Image file too large (maximum 1MB).")

        return profile_picture

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            elearn_user = elearnUser.objects.create(
                user=user, user_type='teacher')
            # Adds the user to the 'teachers' group
            try:
                teachers_group = Group.objects.get(name='Teachers')
                user.groups.add(teachers_group)
            except Group.DoesNotExist:
                # Handles the case where group does not exist
                pass
        return user


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Checks file extension (for allowed image types)
            if not profile_picture.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise forms.ValidationError(
                    "Please upload a valid image file.")

            # Checks file size (limit can be adjusted as needed)
            if profile_picture.size > 2.5 * 1024 * 1024:  # 1MB limit
                raise forms.ValidationError(
                    "Image file too large (maximum 1MB).")

        return profile_picture


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


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['file', 'name', 'description', 'uploader']
        widgets = {'uploader': forms.HiddenInput()}


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']

    # You can customize field widgets or add more validation here if needed
    # For example, to make the rating field a dropdown:
    rating = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)])  # 1 to 5 rating scale


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = StatusUpdate
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'})
        }


class ChatRoomForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = ['chat_name']
