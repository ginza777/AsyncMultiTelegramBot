# Generated by Django 5.0.1 on 2024-01-28 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_remove_telegramprofile_bot_telegramprofile_bot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramprofile',
            name='language',
            field=models.CharField(choices=[('uz', 'Uzbek'), ('en', 'English'), ('ru', 'Russian'), ('es', 'Spanish'), ('fr', 'French'), ('de', 'German')], default='uz', max_length=255, null=True),
        ),
    ]