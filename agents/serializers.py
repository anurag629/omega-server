from rest_framework import serializers
from .models import Script, Execution, AIProvider, Container

class AIProviderSerializer(serializers.ModelSerializer):
    """Serializer for AIProvider model"""
    class Meta:
        model = AIProvider
        fields = ['id', 'name', 'provider_type', 'is_active', 'model_name', 'priority', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        
    def to_representation(self, instance):
        """Remove sensitive fields from response"""
        ret = super().to_representation(instance)
        # Don't include API keys in responses
        ret.pop('api_key', None)
        return ret

class ContainerSerializer(serializers.ModelSerializer):
    """Serializer for Container model"""
    class Meta:
        model = Container
        fields = ['id', 'name', 'image', 'is_active', 'working_dir', 'python_path', 'is_running', 'last_checked', 'created_at', 'updated_at']
        read_only_fields = ['is_running', 'last_checked', 'created_at', 'updated_at']

class ScriptSerializer(serializers.ModelSerializer):
    """Serializer for Script model"""
    provider_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Script
        fields = ['id', 'prompt', 'content', 'scene_class', 'provider', 'provider_name', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'provider_name', 'created_at', 'updated_at']
    
    def get_provider_name(self, obj):
        """Get provider name if provider exists"""
        if obj.provider:
            return obj.provider.name
        return None

class ExecutionSerializer(serializers.ModelSerializer):
    """Serializer for Execution model"""
    container_name = serializers.SerializerMethodField()
    script_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Execution
        fields = ['id', 'script', 'script_id', 'attempt_number', 'container', 'container_name', 'is_successful', 'output', 'error', 'output_path', 'started_at', 'completed_at']
        read_only_fields = ['id', 'script', 'script_id', 'container_name', 'started_at', 'completed_at']
    
    def get_container_name(self, obj):
        """Get container name if container exists"""
        if obj.container:
            return obj.container.name
        return None
    
    def get_script_id(self, obj):
        """Get script ID if script exists"""
        if obj.script:
            return str(obj.script.id)
        return None

class ScriptGenerationSerializer(serializers.Serializer):
    """Serializer for script generation request"""
    prompt = serializers.CharField(required=True)
    provider = serializers.CharField(required=False, allow_null=True)
    auto_execute = serializers.BooleanField(required=False, default=False) 