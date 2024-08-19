from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', blank=True, null=True)
    # Required
    first_name = models.CharField(
        max_length=256, null=False, blank=False)
    # Required
    last_name = models.CharField(
        max_length=256, null=False, blank=False)
    # Required
    email = models.EmailField(
        max_length=256, null=False, blank=False)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='eLearning_users',  # Add related_name here
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='eLearning_users',
        # Add related_name here
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.username


class Teacher(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.username


class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    # Unique course code
    code = models.CharField(max_length=256, unique=True)
    name = models.CharField(max_length=256)
    description = models.TextField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student, blank=True, related_name='enrolled_courses')
    start_date = models.DateField()
    end_date = models.DateField()
    enrollment_status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('closed', 'Closed'),
    ], default='open')

    def __str__(self):
        return self.code + ' - ' + self.name


class Material(models.Model):
    id = models.BigAutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file = models.FileField(upload_to='course_materials/')
    upload_date = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=50, blank=True)


class Feedback(models.Model):
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # Add a rating field
    rating = models.IntegerField()
    comment = models.TextField()


class StatusUpdate(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()


class ChatRoom(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=256, unique=True)
    # Can be either teacher or student
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='chat_rooms')
    chat_log = models.TextField(blank=True)


class Enrollment(models.Model):
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class EnrollmentNotification(models.Model):
    id = models.BigAutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name='teacher')
    read = models.BooleanField(default=False)


class MaterialNotification(models.Model):
    id = models.BigAutoField(primary_key=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
