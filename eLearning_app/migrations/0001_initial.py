# Generated by Django 4.2.15 on 2024-08-20 02:24

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='media/profile_pics')),
                ('first_name', models.CharField(max_length=256)),
                ('last_name', models.CharField(max_length=256)),
                ('email', models.EmailField(max_length=256)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='eLearning_users', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='eLearning_users', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=256, unique=True)),
                ('name', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('enrollment_status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed')], default='open', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='course_materials/')),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('file_type', models.CharField(blank=True, max_length=50)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eLearning_app.course')),
            ],
        ),
        migrations.CreateModel(
            name='elearnUser',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('user_type', models.CharField(choices=[('student', 'Student'), ('teacher', 'Teacher')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='StatusUpdate',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('chat_name', models.CharField(max_length=256, unique=True)),
                ('chat_log', models.TextField(blank=True)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='chat_rooms', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MaterialNotification',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('read', models.BooleanField(default=False)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eLearning_app.material')),
                ('student', models.ForeignKey(limit_choices_to=models.Q(('user_type', 'student')), on_delete=django.db.models.deletion.CASCADE, to='eLearning_app.elearnuser')),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('rating', models.IntegerField()),
                ('comment', models.TextField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eLearning_app.course')),
                ('student', models.ForeignKey(limit_choices_to=models.Q(('user_type', 'student')), on_delete=django.db.models.deletion.CASCADE, to='eLearning_app.elearnuser')),
            ],
        ),
        migrations.CreateModel(
            name='EnrollmentNotification',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('read', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eLearning_app.course')),
                ('student', models.ForeignKey(limit_choices_to=models.Q(('user_type', 'student')), on_delete=django.db.models.deletion.CASCADE, to='eLearning_app.elearnuser')),
                ('teacher', models.ForeignKey(limit_choices_to=models.Q(('user_type', 'teacher')), on_delete=django.db.models.deletion.CASCADE, related_name='teacher', to='eLearning_app.elearnuser')),
            ],
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eLearning_app.course')),
                ('student', models.ForeignKey(limit_choices_to=models.Q(('user_type', 'student')), on_delete=django.db.models.deletion.CASCADE, to='eLearning_app.elearnuser')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(('user_type', 'student')), related_name='enrolled_courses', to='eLearning_app.elearnuser'),
        ),
        migrations.AddField(
            model_name='course',
            name='teacher',
            field=models.ForeignKey(limit_choices_to=models.Q(('user_type', 'teacher')), on_delete=django.db.models.deletion.CASCADE, to='eLearning_app.elearnuser'),
        ),
    ]
