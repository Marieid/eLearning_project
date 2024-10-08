from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.parsers import MultiPartParser
from rest_framework.test import APIClient
from rest_framework import status
from ..models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
import uuid
import pytest
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


class APITestCase(TestCase):
    def setUp(self):
        # Uses DRF's APIClient for API testing
        self.client = APIClient()

        # Create users and elearnUsers using factories
        self.student_user = UserFactory()
        self.teacher_user = UserFactory()
        self.student = ElearnUserFactory(
            user=self.student_user, user_type='student')
        self.teacher = ElearnUserFactory(
            user=self.teacher_user, user_type='teacher')

        # Create a course
        self.course = CourseFactory(teacher=self.teacher)

        # Create other related objects
        self.material = MaterialFactory(
            course=self.course, uploader=self.teacher)
        self.feedback = FeedbackFactory(
            student=self.student, course=self.course)
        self.status_update = StatusUpdateFactory(user=self.student_user)
        self.chat_room = ChatRoomFactory(admin=self.teacher_user)
        self.chat_room.members.add(self.student_user, self.teacher_user)
        self.enrollment = EnrollmentFactory(
            student=self.student, course=self.course)

        # Get tokens for authentication
        student_refresh = RefreshToken.for_user(self.student_user)
        self.student_access_token = str(student_refresh.access_token)

        teacher_refresh = RefreshToken.for_user(self.teacher_user)
        self.teacher_access_token = str(teacher_refresh.access_token)

        # Set the Authorization header with the teacher's token for authenticated requests
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.teacher_access_token)

    def test_get_user_list_unauthorized(self):
        # Test unauthorized access to user list
        url = reverse('user-list')
        response = self.client.get(url)
        # Should be forbidden for non-admin
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_elearnuser_list(self):
        # Authenticate as a student
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.student_access_token}')

        # Test getting the list of elearnUsers (requires authentication)
        url = reverse('elearnuser-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_elearnuser_detail(self):
        # Authenticate as a student
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.student_access_token}')

        # Test getting details of a specific elearnUser
        url = reverse('elearnuser-detail', kwargs={'pk': self.student.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_elearnuser_unauthorized(self):
        # Authenticate as a teacher user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')

        # Attempt to change the user_type only, using PATCH
        data = {'user_type': 'teacher'}

        # Perform the update with PATCH
        url = reverse('elearnuser-detail', kwargs={'pk': self.student.pk})
        response = self.client.patch(url, data, format='json')

        # Should be forbidden since the teacher should not update the student
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_course_authorized(self):
        # Authenticate as a teacher user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')
        url = reverse('course-detail', kwargs={'pk': 1})

        data = {
            'code': 'Check01',
            'name': 'New course updated',
            "description": "Test Description",
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'enrollment_status': 'open'
        }
        # Test course update
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_chat_room_authorized(self):
        # Authenticate as a student user (who is a member of the chat room)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.student_access_token}')

        # Test chat room access
        url = reverse('chatroom-detail', kwargs={'pk': self.chat_room.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.student_user.username,
                      [member['username'] for member in response.data['members']])

    def test_upload_material_authorized(self):
        # Create a dummy file for upload
        dummy_file = SimpleUploadedFile("test_file.txt", b"file content")

        # Authenticate as a teacher user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')

        # Define material data
        data = {
            'name': 'Lecture Notes',
            'description': 'Description for lecture notes',
            'course': self.course.pk,
            'file': dummy_file,
            'uploader': self.teacher.pk,
        }

        # Test material upload
        url = reverse('add_material', kwargs={'course_id': self.course.pk})
        self.client.parser_classes = [MultiPartParser]
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # Follows the redirect
        redirect_url = response['Location']
        response = self.client.get(redirect_url)
        # Assert on the final response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enrollment_unauthorized(self):
        # Authenticate as a teacher user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')

        # Define enrollment data
        data = {
            # Trying to enroll the teacher
            'student': self.teacher.pk,
            'course': self.course.pk,
        }

        # Test unauthorized enrollment
        url = reverse('enrollment-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submit_feedback_authorized(self):
        # Authenticate as a student user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.student_access_token}')

        data = {
            'course': self.course.pk,
            'student': self.student.pk,
            'rating': 5,
            'comment': 'Great course!'
        }

        # Test feedback submission
        url = reverse('submit_feedback', kwargs={'course_id': self.course.pk})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        # Follow the redirect
        redirect_url = response['Location']
        response = self.client.get(redirect_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_submit_feedback_unauthorized(self):
        url = reverse('feedback-list')
        data = {
            "course": self.course.pk,
            "rating": 5,
            "comment": "Great course!"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_list_authorized(self):
        # Make the teacher user a superuser (admin)
        self.teacher_user.is_superuser = True
        self.teacher_user.is_staff = True
        self.teacher_user.save()

        # Authenticate as the admin user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')

        # Test authorized access to user list
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Access the list of users within 'results'
        self.assertIsInstance(response.data['results'], list)

    def test_get_course_list_as_student(self):
        """
        Test that a student can retrieve the list of open courses.
        """

        # Authenticate as a student
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.student_access_token}')

        # Make the request
        url = reverse('course-list')
        response = self.client.get(url)

        # Assert the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the response data is a list (potentially paginated)
        self.assertIsInstance(response.data, dict)
        self.assertIn('results', response.data)  # Check for pagination
        self.assertIsInstance(response.data['results'], list)

    def test_get_course_detail_as_teacher(self):
        """
        Test that a teacher can retrieve the details of a course they teach.
        """

        # Authenticate as the teacher who created the course
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')

        # Make the request
        url = reverse('course-detail', kwargs={'pk': self.course.pk})
        response = self.client.get(url)

        # Assert the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.course.id)
        self.assertEqual(response.data['code'], self.course.code)

    def test_get_chat_room_detail(self):
        """
        Test that an authenticated user can retrieve the details of a chat room.
        """

        # Authenticate as the teacher user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')

        # Make the request
        url = reverse('chatroom-detail', kwargs={'pk': self.chat_room.pk})
        response = self.client.get(url)

        # Assert the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['chat_name'], self.chat_room.chat_name)

    def test_get_enrollments_for_student(self):
        """
        Test that a student can retrieve the list of their enrollments.
        """
        # Authenticate as a student user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.student_access_token}')

        # Make the request to list enrollments
        url = reverse('enrollment-list')
        response = self.client.get(url)

        # Assert the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Since pagination is disabled, expect a single enrollment object
        self.assertIsInstance(response.data, dict)

        # Check if the student's enrollment is in the response
        self.assertEqual(response.data['id'], self.enrollment.id)

    def test_get_material_detail(self):
        """
        Test that an authenticated user can retrieve the details of a material.
        """

        # Authenticate as the teacher user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')

        # Make the request
        url = reverse('material-detail', kwargs={'pk': self.material.pk})
        response = self.client.get(url)

        # Assert the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.material.name)
