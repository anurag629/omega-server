from django.db import models
import uuid
from django.conf import settings


class ManimScript(models.Model):
    """Model to track Manim script generation and execution"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='manim_scripts', null=True)
    prompt = models.TextField(help_text="The user prompt used to generate the script")
    script = models.TextField(help_text="The generated Manim script")
    provider = models.CharField(
        max_length=20, 
        choices=[('gemini', 'Google Gemini'), ('azure_openai', 'Azure OpenAI')],
        help_text="AI provider used for generation"
    )
    output_path = models.CharField(max_length=255, null=True, blank=True, help_text="Path to the output video")
    output_url = models.URLField(max_length=500, null=True, blank=True, help_text="Full URL to access the output video")
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending',
        help_text="Status of the script execution"
    )
    error_message = models.TextField(null=True, blank=True, help_text="Error message if execution failed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.provider} script {self.id} - Status: {self.status}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Manim Script"
        verbose_name_plural = "Manim Scripts" 