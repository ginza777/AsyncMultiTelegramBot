# Generated by Django 5.0.1 on 2024-01-29 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatgpt', '0011_remove_chatgptuser_current_dialog_id_dialog_bot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dialog',
            name='messages',
            field=models.TextField(null=True),
        ),
    ]