from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date
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

        # Create users and elearnUsers
        self.student_user = UserFactory()
        self.teacher_user = UserFactory()
        self.student = ElearnUserFactory(
            user=self.student_user, user_type='student')
        self.teacher = ElearnUserFactory(
            user=self.teacher_user, user_type='teacher')

        # Create a course
        self.course = CourseFactory(teacher=self.teacher)

        # Create other objects
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
        refresh = RefreshToken.for_user(self.student_user)
        self.student_access_token = str(refresh.access_token)
        refresh = RefreshToken.for_user(self.teacher_user)
        self.teacher_access_token = str(refresh.access_token)

    def test_get_user_list_unauthorized(self):
        # Authenticate as a student (non-admin) user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.student_access_token}')

        # Test unauthorized access to user list
        url = reverse('user-list')
        response = self.client.get(url)

        # Should be forbidden for non-admin
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_list_authorized(self):
        # Make the teacher user a superuser (admin)
        self.teacher_user.is_superuser = True
        self.teacher_user.is_staff = True
        self.teacher_user.save()

        # Login as the admin user
        refresh = RefreshToken.for_user(self.teacher_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # Test authorized access to user list
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_get_elearnuser_list(self):
        # Test getting the list of elearnUsers (should require authentication)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.student_access_token}')
        url = reverse('elearnuser-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_elearnuser_detail(self):
        # Test getting details of a specific elearnUser
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.student_access_token}')
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

    def test_create_course_authorized(self):
        # Authenticate as a teacher user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')

        # Define course data
        data = {
            'code': 'CS101',
            'name': 'Introduction to Computer Science',
            'teacher': self.teacher.pk,
            'start_date': '2024-03-01',
            'end_date': '2025-05-01',
        }

        # Test course creation
        url = reverse('course-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'],
                         'Introduction to Computer Science')

    def test_create_course_unauthorized(self):
        # Authenticate as a student user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.student_access_token}')

        # Define course data
        data = {
            'code': 'CS101',
            'name': 'Introduction to Computer Science',
            'teacher': self.teacher.pk,
            'start_date': '2024-09-01',
            'start_date': '2025-03-01'
        }

        # Test course creation
        url = reverse('course-list')
        response = self.client.post(url, data, format='json')

        # Should be forbidden for students
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_course_authorized(self):
        # Authenticate as a teacher user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')

        # Define updated course data
        data = {
            'name': 'Advanced Computer Science'
        }

        # Test course update
        url = reverse('course-detail', kwargs={'pk': self.course.pk})
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Advanced Computer Science')

    def test_access_chat_room_authorized(self):
        # Authenticate as a student user (who is a member of the chat room)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.student_access_token}')

        # Test chat room access
        url = reverse('chatroom-detail', kwargs={'pk': self.chat_room.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.student_user.username,
                      response.data['members'][0]['username'])

    def test_upload_material_authorized(self):
        # Authenticate as a teacher user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')

        # Define material data
        data = {
            'name': 'Test Material',
            'description': 'Description for test material',
            'course': self.course.id,
            # uploader is a ForeignKey to ElearnUser
            'uploader': self.teacher.user.pk,
        }

        # Test material upload
        url = reverse('material-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Lecture Notes')

    def test_enrollment_authorized(self):
        # Authenticate as a student user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.student_access_token}')

        # Define enrollment data
        data = {
            'student': self.student.pk,
            'course': self.course.pk,
        }

        # Test enrollment
        url = reverse('enrollment-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['course']['id'], self.course.pk)

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

        # Test enrollment
        url = reverse('enrollment-list')
        response = self.client.post(url, data, format='json')

        # Should be forbidden for teachers
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_material_authorized(self):
        # Authenticate as the teacher user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')

        # Data for creating a material
        data = {
            'title': 'New Material',
            'description': 'Material for the test course',
            'course': self.course.pk,  # Link this material to the existing course
            'uploader': self.teacher.pk,
            'file': None,  # Assuming there's a file field; set to None or use a mock file
        }

        # Test authorized creation of material
        url = reverse('material-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_submit_feedback_authorized(self):
        # Authenticate as a student user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.student_access_token}')

        # Define feedback data
        data = {
            'course_id': self.course.pk,
            'student': self.student.pk,
            'rating': 5,
            'comment': 'Great course!'
        }

        # Test feedback submission
        url = reverse('feedback-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['comment'], 'Great course!')

    def test_submit_feedback_unauthorized(self):
        # Authenticate as a teacher user
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.teacher_access_token}')

        # Define feedback data
        data = {
            'course_id': self.course.pk,
            'student': self.student.pk,
            'rating': 5,
            'comment': 'Great course!'
        }

        # Test feedback submission
        url = reverse('feedback-list')
        response = self.client.post(url, data, format='json')

        # Should be forbidden for teachers
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
