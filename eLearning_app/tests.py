from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Student, Teacher, Course


class UserModelTestCase(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', password='testpassword',
                                        first_name='John', last_name='Doe', email='john.doe@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpassword'))

    def test_create_student(self):
        user = User.objects.create_user(username='teststudent', password='testpassword',
                                        first_name='Jane', last_name='Smith', email='jane.smith@example.com',
                                        is_student=True)
        student = Student.objects.create(user=user)
        self.assertEqual(student.user.username, 'teststudent')

    def test_create_teacher(self):
        # Similar to test_create_student, but for Teacher
        pass


class CourseModelTestCase(TestCase):
    def test_create_course(self):
        teacher = Teacher.objects.create(user=User.objects.create_user(
            username='testteacher', password='testpassword', first_name='Alice', last_name='Johnson', email='alice.johnson@example.com', is_teacher=True
        ))
        course = Course.objects.create(code='CM101', name='Introduction to Computer Science',
                                       description='A beginner-friendly course on computer science fundamentals.',
                                       teacher=teacher)
        self.assertEqual(course.code, 'CM101')
        self.assertEqual(course.teacher, teacher)


class ViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword',
                                             first_name='John', last_name='Doe', email='john.doe@example.com')
        self.student = Student.objects.create(user=self.user)
        self.teacher = Teacher.objects.create(user=User.objects.create_user(
            username='testteacher', password='testpassword', first_name='Alice', last_name='Johnson', email='alice.johnson@example.com', is_teacher=True
        ))
        self.course = Course.objects.create(code='CM101', name='Introduction to Computer Science',
                                            description='A beginner-friendly course on computer science fundamentals.',
                                            teacher=self.teacher)

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'eLearning_app/index.html')

    def test_register_student_view(self):
        # Test GET request
        response = self.client.get(reverse('register_student'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'eLearning_app/register_student.html')

        # Test POST request (successful registration)
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
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(User.objects.filter(username='newstudent').exists())

    def test_register_teacher_view(self):
        # Similar to test_register_student_view, but for Teacher
        pass

    def test_login_view(self):
        # Test GET request
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'eLearning_app/login.html')

        # Test POST request (successful login)
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code,
                         302)  # Redirect after successful login
        self.assertRedirects(response, reverse('index'))

    def test_create_course_view(self):
        # Test unauthorized access (student trying to create a course)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('create_course'))
        # Redirect to index due to lack of permission
        self.assertEqual(response.status_code, 302)

        # Test authorized access (teacher creating a course)
        self.client.login(username='testteacher', password='testpassword')
        response = self.client.get(reverse('create_course'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'eLearning_app/create_course.html')

        # Test POST request (successful course creation)
        data = {
            'code': 'CM202',
            'name': 'Advanced Web Development',
            'description': 'An advanced course on web development.',
            'start_date': '2024-09-01',
            'end_date': '2024-12-31'
        }
        response = self.client.post(reverse('create_course'), data)
        self.assertEqual(response.status_code, 302)
        # Assuming the new course has id=2
        self.assertRedirects(response, reverse('course_detail', kwargs={
                             'course_id': 2}))
        self.assertTrue(Course.objects.filter(code='CM202').exists())
