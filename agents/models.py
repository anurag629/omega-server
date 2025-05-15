from django.db import models
from django.utils import timezone
import uuid

class AIProvider(models.Model):
    """Model for AI providers used for script generation and debugging"""
    PROVIDER_CHOICES = [
        ('gemini', 'Google Gemini'),
        ('azure_openai', 'Azure OpenAI'),
        ('openai', 'OpenAI')
    ]
    
    name = models.CharField(max_length=100)
    provider_type = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    api_key = models.CharField(max_length=255)
    endpoint = models.URLField(blank=True, null=True)  # For Azure OpenAI
    deployment = models.CharField(max_length=100, blank=True, null=True)  # For Azure OpenAI
    model_name = models.CharField(max_length=100, default="gemini-2.5-flash-preview-04-17")
    is_active = models.BooleanField(default=True)
    
    # Preference order for fallback (lower is preferred)
    priority = models.IntegerField(default=10)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority']
    
    def __str__(self):
        return f"{self.name} ({self.provider_type})"

class Container(models.Model):
    """Model for Docker container configurations"""
    name = models.CharField(max_length=100, unique=True)
    image = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    
    # Container settings
    working_dir = models.CharField(max_length=255, default="/manim")
    python_path = models.CharField(max_length=255, default="python")
    
    # Container status
    is_running = models.BooleanField(default=False)
    last_checked = models.DateTimeField(default=timezone.now)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({'Running' if self.is_running else 'Stopped'})"

class Script(models.Model):
    """Model for storing generated Manim scripts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt = models.TextField()
    content = models.TextField()
    scene_class = models.CharField(max_length=100, null=True, blank=True)
    
    # Relationship to the AI provider that generated it
    provider = models.ForeignKey(
        AIProvider, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='generated_scripts'
    )
    
    # Script status
    STATUS_CHOICES = [
        ('pending', 'Pending Execution'),
        ('executing', 'Executing'),
        ('successful', 'Successfully Executed'),
        ('failed', 'Execution Failed'),
        ('debugging', 'Being Debugged')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # When was the script generated and last modified
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Script {self.id} - {self.scene_class or 'Unknown'}"

class Execution(models.Model):
    """Model for tracking script execution attempts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    script = models.ForeignKey(Script, on_delete=models.CASCADE, related_name='executions')
    
    # Attempt details
    attempt_number = models.IntegerField(default=1)
    container = models.ForeignKey(Container, on_delete=models.SET_NULL, null=True)
    
    # Result details
    is_successful = models.BooleanField(default=False)
    output = models.TextField(blank=True)
    error = models.TextField(blank=True)
    
    # Output file path (relative to MEDIA_ROOT)
    output_path = models.CharField(max_length=255, blank=True)
    
    # Execution timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Any modifications made by debugging
    original_script = models.TextField(blank=True)
    modified_script = models.TextField(blank=True)
    
    def __str__(self):
        return f"Execution {self.id} - Attempt #{self.attempt_number} - {'Success' if self.is_successful else 'Failed'}"
