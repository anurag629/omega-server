# Generated by Django 5.2.1 on 2025-05-15 15:32

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AIProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('provider_type', models.CharField(choices=[('gemini', 'Google Gemini'), ('azure_openai', 'Azure OpenAI'), ('openai', 'OpenAI')], max_length=20)),
                ('api_key', models.CharField(max_length=255)),
                ('endpoint', models.URLField(blank=True, null=True)),
                ('deployment', models.CharField(blank=True, max_length=100, null=True)),
                ('model_name', models.CharField(default='gemini-2.5-flash-preview-04-17', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('priority', models.IntegerField(default=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['priority'],
            },
        ),
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('image', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('working_dir', models.CharField(default='/manim', max_length=255)),
                ('python_path', models.CharField(default='python', max_length=255)),
                ('is_running', models.BooleanField(default=False)),
                ('last_checked', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('prompt', models.TextField()),
                ('content', models.TextField()),
                ('scene_class', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending Execution'), ('executing', 'Executing'), ('successful', 'Successfully Executed'), ('failed', 'Execution Failed'), ('debugging', 'Being Debugged')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('provider', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='generated_scripts', to='agents.aiprovider')),
            ],
        ),
        migrations.CreateModel(
            name='Execution',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('attempt_number', models.IntegerField(default=1)),
                ('is_successful', models.BooleanField(default=False)),
                ('output', models.TextField(blank=True)),
                ('error', models.TextField(blank=True)),
                ('output_path', models.CharField(blank=True, max_length=255)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('original_script', models.TextField(blank=True)),
                ('modified_script', models.TextField(blank=True)),
                ('container', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='agents.container')),
                ('script', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='executions', to='agents.script')),
            ],
        ),
        
        # Add default container
        migrations.RunPython(
            code=lambda apps, schema_editor: apps.get_model('agents', 'Container').objects.create(
                name='omega-manim',
                image='manim/manim:latest',
                is_active=True,
                working_dir='/manim',
                python_path='python',
                is_running=False
            ),
            reverse_code=lambda apps, schema_editor: apps.get_model('agents', 'Container').objects.filter(name='omega-manim').delete()
        ),
    ] 