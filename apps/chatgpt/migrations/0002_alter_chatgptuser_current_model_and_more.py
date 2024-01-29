# Generated by Django 5.0.1 on 2024-01-25 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatgpt', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatgptuser',
            name='current_model',
            field=models.CharField(choices=[('gpt-3.5-turbo', 'GPT-3.5 Turbo'), ('gpt-3.5-turbo-16k', 'GPT-3.5 Turbo 16k'), ('gpt-4-1106-preview', 'GPT-4 1106 Preview'), ('gpt-4', 'GPT-4'), ('text-davinci-003', 'Text Davinci 003')], default='gpt-3.5-turbo', max_length=255),
        ),
        migrations.AlterField(
            model_name='chatgptuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='chatgptuser',
            name='first_seen',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='chatgptuser',
            name='last_interaction',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='chatgptuser',
            name='n_generated_images',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='chatgptuser',
            name='n_transcribed_seconds',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
        migrations.AlterField(
            model_name='chatgptuser',
            name='n_used_tokens',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='chatgptuser',
            name='username',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]