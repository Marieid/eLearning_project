# Generated by Django 4.2.15 on 2024-08-21 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eLearning_app', '0002_material_description_material_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='name',
            field=models.CharField(default='Untitled Material', max_length=255),
        ),
    ]
