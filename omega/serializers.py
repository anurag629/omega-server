from rest_framework import serializers
from .models import ManimScript


class ManimScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManimScript
        fields = ['id', 'prompt', 'script', 'provider', 'script_path', 
                  'output_path', 'output_url', 'status', 'error_message', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'script', 'script_path', 'output_path', 
                           'output_url', 'status', 'error_message', 
                           'created_at', 'updated_at']


class ManimScriptGenerateSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True, help_text="Description for the Manim animation")
    provider = serializers.ChoiceField(
        choices=['gemini', 'azure_openai'], 
        required=True,
        help_text="AI provider to use for generation"
    )
    execute = serializers.BooleanField(
        required=False, 
        default=False,
        help_text="Whether to execute the script after generation"
    ) 