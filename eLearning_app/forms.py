from .models import Feedback
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission
from .models import User, Course, elearnUser, Material, Feedback, StatusUpdate, ChatRoom


class StudentRegistrationForm(UserCreationForm):
    """Form for registering a new student user, including profile picture validation."""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('first_name', 'last_name', 'email', 'profile_picture')

    def clean_profile_picture(self):
        """Validate the profile picture for correct file type and size."""
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if not profile_picture.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise forms.ValidationError(
                    "Please upload a valid image file.")
            if profile_picture.size > 2.5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Image file too large (maximum 1MB).")
        return profile_picture

    def save(self, commit=True):
        """Save the student user and assign to 'Students' group."""
        user = super().save(commit=False)
        if commit:
            user.save()
            elearnUser.objects.create(user=user, user_type='student')
            students_group = Group.objects.get(name='Students')
            user.groups.add(students_group)
        return user


class TeacherRegistrationForm(UserCreationForm):
    """Form for registering a new teacher user, including profile picture validation."""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('first_name', 'last_name', 'email', 'profile_picture')

    def clean_profile_picture(self):
        """Validate the profile picture for correct file type and size."""
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if not profile_picture.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise forms.ValidationError(
                    "Please upload a valid image file.")
            if profile_picture.size > 2.5 * 1024 * 1024:
                raise forms.ValidationError(
                    "Image file too large (maximum 1MB).")
        return profile_picture

    def save(self, commit=True):
        """Save the teacher user and assign to 'Teachers' group."""
        user = super().save(commit=False)
        if commit:
            user.save()
            elearn_user = elearnUser.objects.create(
                user=user, user_type='teacher')
            try:
                teachers_group = Group.objects.get(name='Teachers')
                user.groups.add(teachers_group)
            except Group.DoesNotExist:
                pass
        return user


class UserProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile information."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Add your profile picture here'})
        }

    def clean_profile_picture(self):
        """Validate the profile picture for correct file type and size."""
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            if not profile_picture.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise forms.ValidationError(
                    "Please upload a valid image file.")
            if profile_picture.size > 2.5 * 1024 * 1024:  # 1MB limit
                raise forms.ValidationError(
                    "Image file too large (maximum 1MB).")
        return profile_picture


class CourseCreationForm(forms.ModelForm):
    """Form for creating a new course."""
    class Meta:
        model = Course
        fields = ['code', 'name', 'description', 'start_date', 'end_date']
    start_date = forms.DateField(widget=forms.DateInput(
        attrs={'placeholder': 'yyyy-mm-dd'}))
    end_date = forms.DateField(widget=forms.DateInput(
        attrs={'placeholder': 'yyyy-mm-dd'}))
    enrollment_status = forms.ChoiceField(
        choices=Course._meta.get_field('enrollment_status').choices)


class MaterialForm(forms.ModelForm):
    """Form for uploading course materials."""
    class Meta:
        model = Material
        fields = ['file', 'name', 'description', 'uploader']
        widgets = {'uploader': forms.HiddenInput()}


class FeedbackForm(forms.ModelForm):
    """Form for submitting feedback on a course."""
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
    rating = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)])  # 1 to 5 rating scale


class StatusUpdateForm(forms.ModelForm):
    """Form for posting status updates."""
    class Meta:
        model = StatusUpdate
        fields = ['content']
        widgets = {'content': forms.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'Write your status update...'})}


class ChatRoomForm(forms.ModelForm):
    """Form for creating a new chat room."""
    class Meta:
        model = ChatRoom
        fields = ['chat_name']
        widgets = {'chat_name': forms.TextInput(
            attrs={'placeholder': 'Enter chat room name'})}

    def clean_chat_name(self):
        """Ensure the chat room name is a single word."""
        chat_name = self.cleaned_data.get('chat_name')
        if ' ' in chat_name:
            raise forms.ValidationError(
                "Chat room name must be a single word.")
        return chat_name
