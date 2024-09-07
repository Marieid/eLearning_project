from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from your_app.models import Course, elearnUser, Material, Feedback, StatusUpdate, ChatRoom
from your_app.forms import (StudentRegistrationForm, TeacherRegistrationForm,
                            CourseCreationForm, MaterialForm, FeedbackForm,
                            StatusUpdateForm, ChatRoomForm)


class Command(BaseCommand):
    help = 'Populate the database with dummy data'

    def handle(self, *args, **options):
        # Create groups if they don't exist
        Group.objects.get_or_create(name='Students')
        Group.objects.get_or_create(name='Teachers')

        # Sample student and teacher data
        student_data = {
            'username': 'student1',
            'password': 'password123',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            # Add 'profile_picture' field if you have sample image data
        }

        teacher_data = {
            'username': 'teacher1',
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            # Add 'profile_picture' field if you have sample image data
        }

        # Create student and teacher users
        student_form = StudentRegistrationForm(student_data)
        if student_form.is_valid():
            student_form.save()
            self.stdout.write(self.style.SUCCESS(
                'Successfully created student user'))
        else:
            self.stdout.write(self.style.ERROR(
                f'Error creating student: {student_form.errors}'))

        teacher_form = TeacherRegistrationForm(teacher_data)
        if teacher_form.is_valid():
            teacher_form.save()
            self.stdout.write(self.style.SUCCESS(
                'Successfully created teacher user'))
        else:
            self.stdout.write(self.style.ERROR(
                f'Error creating teacher: {teacher_form.errors}'))

        # Sample course data (you can reuse the 'courses' list from previous responses)
        # ...

        # Create courses
        for course_data in courses:
            form = CourseCreationForm(course_data)
            if form.is_valid():
                form.save()
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully created course: {course_data["name"]}'))
            else:
                self.stdout.write(self.style.ERROR(
                    f'Error creating course: {form.errors}'))

        # Add more data creation logic for Material, Feedback, StatusUpdate, ChatRoom as needed
        # ...
