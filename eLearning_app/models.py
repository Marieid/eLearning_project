from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    profile_picture = models.ImageField(
        upload_to='media/profile_pics', blank=True, null=True)
    first_name = models.CharField(max_length=256, null=False, blank=False)
    last_name = models.CharField(max_length=256, null=False, blank=False)
    email = models.EmailField(max_length=256,
                              null=False, blank=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='eLearning_users',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='eLearning_users',

        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class elearnUser(models.Model):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.user.username


class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    # Unique course code
    code = models.CharField(max_length=256, unique=True)
    name = models.CharField(max_length=256)
    description = models.TextField()
    teacher = models.ForeignKey(
        elearnUser, on_delete=models.CASCADE, limit_choices_to=Q(user_type='teacher'))
    students = models.ManyToManyField(
        elearnUser, blank=True, related_name='enrolled_courses', limit_choices_to=Q(user_type='student'))
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
    # Use elearnUser for student, limiting choices to students only
    student = models.ForeignKey(
        elearnUser, on_delete=models.CASCADE, limit_choices_to=Q(user_type='student'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()


class StatusUpdate(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()


class ChatRoom(models.Model):
    id = models.BigAutoField(primary_key=True)
    chat_name = models.CharField(max_length=256, unique=True)
    # Can be either teacher or student
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='chat_rooms')
    chat_log = models.TextField(blank=True)


class Enrollment(models.Model):
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(
        elearnUser, on_delete=models.CASCADE, limit_choices_to=Q(user_type='student'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class EnrollmentNotification(models.Model):
    id = models.BigAutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(
        elearnUser, on_delete=models.CASCADE, limit_choices_to=Q(user_type='student'))
    teacher = models.ForeignKey(elearnUser, on_delete=models.CASCADE,
                                related_name='teacher', limit_choices_to=Q(user_type='teacher'))
    read = models.BooleanField(default=False)


class MaterialNotification(models.Model):
    id = models.BigAutoField(primary_key=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    student = models.ForeignKey(
        elearnUser, on_delete=models.CASCADE, limit_choices_to=Q(user_type='student'))
    read = models.BooleanField(default=False)
