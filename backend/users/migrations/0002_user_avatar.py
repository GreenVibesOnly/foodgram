# Generated by Django 5.0.6 on 2024-07-12 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='media/users/', verbose_name='Аватар'),
        ),
    ]
