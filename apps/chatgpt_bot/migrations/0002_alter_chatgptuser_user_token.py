# Generated by Django 5.0.1 on 2024-01-31 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatgpt_bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatgptuser',
            name='user_token',
            field=models.CharField(blank=True, default='377c6aaa80ac4a24aa946a7d79f44039', max_length=255, null=True),
        ),
    ]