# Generated by Django 5.0.1 on 2024-02-23 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot_main_setup', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackupSenderBot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=200, unique=True)),
                ('channel_id', models.CharField(max_length=200, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]