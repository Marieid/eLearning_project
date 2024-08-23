from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Group, Permission
from .models import User, elearnUser, Course, Material, Enrollment, Feedback, StatusUpdate
from .forms import ChatRoomForm, CourseCreationForm, FeedbackForm, MaterialForm, StatusUpdateForm, StudentRegistrationForm
from django.core.files.uploadedfile import SimpleUploadedFile
from .factories import (
    UserFactory,
    ElearnUserFactory,
    CourseFactory,
    MaterialFactory,
    FeedbackFactory,
    StatusUpdateFactory,
    ChatRoomFactory,
    MessageFactory,
    EnrollmentFactory,
    EnrollmentNotificationFactory,
    MaterialNotificationFactory,
)


class ElearningAppTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create groups and permissions
        self.student_group, _ = Group.objects.get_or_create(name='Students')
        self.teacher_group, _ = Group.objects.get_or_create(name='Teachers')

        add_course_perm = Permission.objects.get(codename='add_course')
        self.teacher_group.permissions.add(add_course_perm)

        # Create users using factories
        self.student_user = UserFactory()
        self.teacher_user = UserFactory()

        # Create elearnUser objects and assign to groups
        self.student = ElearnUserFactory(
            user=self.student_user, user_type='student')
        self.student_user.groups.add(self.student_group)
        self.teacher = ElearnUserFactory(
            user=self.teacher_user, user_type='teacher')
        self.teacher_user.groups.add(self.teacher_group)

        # Create a course using factory
        self.course = CourseFactory(teacher=self.teacher)

    def test_user_str(self):
        self.assertEqual(
            str(self.user), f"{self.user.first_name} {self.user.last_name}")

    def test_elearnuser_str(self):
        self.assertEqual(str(self.elearn_user), self.elearn_user.user.username)

    def test_course_str(self):
        self.assertEqual(str(self.course),
                         f"{self.course.code} - {self.course.name}")

    def test_chatroom_str(self):
        self.assertEqual(str(self.chat_room), self.chat_room.chat_name)

    def test_message_str(self):
        expected_str = f"{self.message.user.username}: {self.message.content[:20]}"
        self.assertEqual(str(self.message), expected_str)

    # Add more model tests here to cover relationships, field constraints, etc.
    def test_course_teacher_relationship(self):
        self.assertEqual(self.course.teacher.user_type, 'teacher')

    def test_course_students_relationship(self):
        self.course.students.add(self.elearn_user)
        self.assertIn(self.elearn_user, self.course.students.all())

    def test_material_course_relationship(self):
        self.assertEqual(self.material.course, self.course)

    def test_material_file_upload(self):
        file = SimpleUploadedFile("testfile.txt", b"file_content")
        material = MaterialFactory(course=self.course, file=file)
        self.assertEqual(material.file.read(), b"file_content")

    def test_feedback_course_relationship(self):
        self.assertEqual(self.feedback.course, self.course)

    def test_feedback_student_relationship(self):
        self.assertEqual(self.feedback.student.user_type, 'student')

    def test_status_update_user_relationship(self):
        self.assertEqual(self.status_update.user, self.user)

    def test_enrollment_student_relationship(self):
        self.assertEqual(self.enrollment.student.user_type, 'student')

    def test_enrollment_course_relationship(self):
        self.assertEqual(self.enrollment.course, self.course)

    def test_enrollmentnotification_relationships(self):
        self.assertEqual(self.enrollment_notification.course, self.course)
        self.assertEqual(
            self.enrollment_notification.student.user_type, 'student')
        self.assertEqual(
            self.enrollment_notification.teacher.user_type, 'teacher')

    def test_materialnotification_relationships(self):
        self.assertEqual(self.material_notification.material, self.material)
        self.assertEqual(
            self.material_notification.student.user_type, 'student')


class FormTests(TestCase):
    def test_student_registration_form_valid(self):
        form_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
        }
        form = StudentRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_teacher_registration_form_valid(self):
        # Similar to test_student_registration_form_valid but for TeacherRegistrationForm
        pass

    def test_course_creation_form_valid(self):
        form_data = {
            'code': 'TEST202',
            'name': 'Another Test Course',
            'description': 'This is another test course',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'enrollment_status': 'open'
        }
        form = CourseCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_material_form_valid(self):
        file = SimpleUploadedFile("testfile.txt", b"file_content")
        # Test with a valid file upload
        with open(file, 'rb') as f:
            file_data = f.read()
        file = SimpleUploadedFile("test_file.txt", file_data)
        form_data = {
            'file': file,
            'name': 'Test Material',
            'description': 'Description for test material'
        }
        form = MaterialForm(data=form_data, files={'file': file})
        self.assertTrue(form.is_valid())

    def test_feedback_form_valid(self):
        form_data = {
            'rating': 4,
            'comment': 'This is a test feedback comment.'
        }
        form = FeedbackForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_status_update_form_valid(self):
        form_data = {
            'content': 'This is a test status update.'
        }
        form = StatusUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_chat_room_form_valid(self):
        form_data = {
            'chat_name': 'Test Chat Room'
        }
        form = ChatRoomForm(data=form_data)
        self.assertTrue(form.is_valid())


class IdentificationAndRegistrationTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Create groups and permissions
        self.student_group, _ = Group.objects.get_or_create(name='Students')
        self.teacher_group, _ = Group.objects.get_or_create(name='Teachers')

        add_course_perm = Permission.objects.get(codename='add_course')
        self.teacher_group.permissions.add(add_course_perm)

    def test_register_student(self):
        data = {
            'username': 'newstudent',
            'password': 'newpassword',
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'newstudent@example.com'
        }
        response = self.client.post(reverse('register_student'), data)
        # Redirect after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        # Check if the user and elearnUser were created
        new_user = User.objects.get(username='newstudent')
        self.assertTrue(hasattr(new_user, 'elearnuser'))
        self.assertEqual(new_user.elearnuser.user_type, 'student')

        # Check if the user was added to the 'students' group
        self.assertIn(self.student_group, new_user.groups.all())

    def test_register_teacher(self):
        data = {
            'username': 'newteacher',
            'password': 'newpassword',
            'first_name': 'Teach',
            'last_name': 'Teacher',
            'email': 'newteacher@example.com'
        }
        response = self.client.post(reverse('register_teacher'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

        new_user = User.objects.get(username='newteacher')
        self.assertTrue(hasattr(new_user, 'elearnuser'))
        self.assertEqual(new_user.elearnuser.user_type, 'teacher')

        self.assertIn(self.teacher_group, new_user.groups.all())

    def test_login(self):
        data = {'username': 'teststudent', 'password': 'testpassword'}
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
