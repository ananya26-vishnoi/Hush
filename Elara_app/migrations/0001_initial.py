# Generated by Django 5.0.1 on 2024-01-08 04:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=1000)),
                ('username', models.CharField(max_length=1000)),
                ('otp', models.CharField(blank=True, max_length=1000, null=True)),
                ('otp_verified', models.BooleanField(default=False)),
                ('private_key', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Index',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index_id', models.CharField(max_length=1000)),
                ('file_folder_name', models.CharField(max_length=1000)),
                ('last_chat_time', models.DateTimeField(auto_now=True)),
                ('all_files', models.CharField(blank=True, max_length=10000000, null=True)),
                ('all_data', models.TextField(blank=True, null=True)),
                ('chat_type', models.CharField(blank=True, max_length=1000, null=True)),
                ('chat_history', models.JSONField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Elara_app.user')),
            ],
        ),
    ]
