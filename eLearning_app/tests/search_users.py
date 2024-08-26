from django.test import TestCase
from django.urls import reverse
from .factories import *


class SearchUsersTestCase(TestCase):
    def setUp(self):
        # Create some test users and elearnUsers
        self.user1 = UserFactory(
            username='john_doe', first_name='John', last_name='Doe')
        self.user2 = UserFactory(
            username='jane_smith', first_name='Jane', last_name='Smith')
        self.elearn_user1 = ElearnUserFactory(
            user=self.user1, user_type='student')
        self.elearn_user2 = ElearnUserFactory(
            user=self.user2, user_type='teacher')

    def test_search_by_username(self):
        response = self.client.get(reverse('search_users'), {'q': 'john'})
        self.assertEqual(response.status_code, 200)
        # Check if user1 is in the results
        self.assertContains(response, 'john_doe')
        # Check if user2 is NOT in the results
        self.assertNotContains(response, 'jane_smith')

    def test_search_by_first_name(self):
        response = self.client.get(reverse('search_users'), {
                                   'q': 'Ja'})  # Partial match
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'jane_smith')

    def test_search_by_last_name_case_insensitive(self):
        response = self.client.get(reverse('search_users'), {
                                   'q': 'doe'})  # Lowercase
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'john_doe')

    def test_search_within_elearnuser(self):
        response = self.client.get(reverse('search_users'), {'q': 'teacher'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'jane_smith')

    def test_empty_query(self):
        response = self.client.get(reverse('search_users'), {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['users'], [])  # No results

    def test_no_duplicates(self):
        # Create another elearnUser with the same username as user1
        ElearnUserFactory(user=self.user1, user_type='teacher')

        response = self.client.get(reverse('search_users'), {'q': 'john'})
        self.assertEqual(response.status_code, 200)
        # Only one John Doe should be returned
        self.assertEqual(len(response.context['users']), 1)


class UserProfileTestCase(TestCase):
    def setUp(self):
        # Create test users and elearnUsers
        self.student_user = UserFactory(username='teststudent')
        self.teacher_user = UserFactory(username='testteacher')
        self.student = ElearnUserFactory(
            user=self.student_user, user_type='student')
        self.teacher = ElearnUserFactory(
            user=self.teacher_user, user_type='teacher')

        # Create a course and enroll the student
        self.course = CourseFactory(teacher=self.teacher)
        EnrollmentFactory(student=self.student, course=self.course)

    def test_student_profile(self):
        # ... (logic to log in as self.student_user)

        response = self.client.get(reverse('user_profile_detail', kwargs={
                                   'user_id': self.student_user.id}))
        self.assertEqual(response.status_code, 200)

        # Check for student-specific information
        self.assertContains(response, 'teststudent')
        self.assertContains(response, 'Enrolled Courses')
        # Check if the enrolled course is displayed
        self.assertContains(response, self.course.name)

    def test_teacher_profile(self):
        # ... (logic to log in as self.teacher_user)

        response = self.client.get(reverse('user_profile_detail', kwargs={
                                   'user_id': self.teacher_user.id}))
        self.assertEqual(response.status_code, 200)

        # Check for teacher-specific information
        self.assertContains(response, 'testteacher')
        self.assertContains(response, 'Courses Taught')
        self.assertContains(response, self.course.name)

    def test_nonexistent_user(self):
        response = self.client.get(reverse('user_profile_detail', kwargs={
                                   'user_id': 999}))  # Non-existent ID
        # Or handle it gracefully in your view and assert accordingly
        self.assertEqual(response.status_code, 404)
