from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    profile_picture = models.ImageField(
        upload_to='profile_pics', blank=True, null=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=256)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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
    code = models.CharField(max_length=256, unique=True)
    name = models.CharField(max_length=256)
    description = models.TextField()
    teacher = models.ForeignKey(
        elearnUser, on_delete=models.CASCADE, limit_choices_to=Q(user_type='teacher'))
    students = models.ManyToManyField(
        elearnUser, blank=True, related_name='enrolled_courses', limit_choices_to=Q(user_type='student'))
    start_date = models.DateField()
    end_date = models.DateField()
    enrollment_status = models.CharField(max_length=20, choices=[(
        'open', 'Open'), ('closed', 'Closed')], default='open')
    blocked_students = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='blocked_courses', blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Material(models.Model):
    id = models.BigAutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file = models.FileField(upload_to='course_materials/')
    uploader = models.ForeignKey(elearnUser, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=255, default="Untitled Material")
    description = models.TextField(blank=True)


class Feedback(models.Model):
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(
        elearnUser, on_delete=models.CASCADE, limit_choices_to=Q(user_type='student'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # Ensures rating is positive
    rating = models.PositiveIntegerField()
    comment = models.TextField()


class StatusUpdate(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()


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


class ChatRoom(models.Model):
    id = models.BigAutoField(primary_key=True)
    chat_name = models.CharField(max_length=256, unique=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='chat_rooms')

    def __str__(self):
        return self.chat_name


class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}'


@receiver(post_save, sender=Enrollment)
def create_enrollment_notification(sender, instance, created, **kwargs):
    if created:
        EnrollmentNotification.objects.create(
            course=instance.course,
            student=instance.student,
            teacher=instance.course.teacher
        )


@receiver(post_save, sender=Material)
def create_material_notification(sender, instance, created, **kwargs):
    if created:
        for student in instance.course.students.all():
            MaterialNotification.objects.create(
                material=instance,
                student=student
            )


class BlockNotification(models.Model):
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(
        elearnUser, on_delete=models.CASCADE, limit_choices_to=Q(user_type='student'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blocked Notification for {self.student.user.username} in {self.course.name}"
