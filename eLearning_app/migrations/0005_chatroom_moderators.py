# Generated by Django 4.2.15 on 2024-09-07 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eLearning_app', '0004_blocknotification_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='moderators',
            field=models.ManyToManyField(blank=True, limit_choices_to=models.Q(('user_type', 'teacher')), related_name='moderated_chat_rooms', to='eLearning_app.elearnuser'),
        ),
    ]