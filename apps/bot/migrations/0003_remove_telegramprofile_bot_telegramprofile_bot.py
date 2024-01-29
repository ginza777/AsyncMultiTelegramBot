# Generated by Django 5.0.1 on 2024-01-28 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_telegramprofile_is_bot'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telegramprofile',
            name='bot',
        ),
        migrations.AddField(
            model_name='telegramprofile',
            name='bot',
            field=models.ManyToManyField(to='bot.telegrambot'),
        ),
    ]