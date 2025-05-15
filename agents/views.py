from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Script, Execution, AIProvider, Container
from .agents.ai_agent import AIScriptGenerationAgent
from .agents.execution_agent import ManimExecutionAgent
from .serializers import (
    ScriptSerializer,
    ExecutionSerializer,
    AIProviderSerializer,
    ContainerSerializer,
    ScriptGenerationSerializer
)

class ScriptViewSet(viewsets.ModelViewSet):
    """API endpoint for Manim scripts"""
    queryset = Script.objects.all()
    serializer_class = ScriptSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute the script"""
        script = self.get_object()
        
        # Create execution agent
        execution_agent = ManimExecutionAgent()
        
        # Execute the script
        result = execution_agent.execute(script)
        
        # Return the result
        if result['success']:
            return Response({
                'success': True,
                'message': 'Script executed successfully',
                'output_path': result['output_path'],
                'execution_id': result['execution'].id if 'execution' in result else None
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Script execution failed',
                'error': result.get('error', 'Unknown error'),
                'execution_id': result['execution'].id if 'execution' in result else None
            }, status=status.HTTP_200_OK)  # Still return 200 as the API call succeeded
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new script from a prompt"""
        # Validate input
        serializer = ScriptGenerationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get parameters
        prompt = serializer.validated_data['prompt']
        provider_id = serializer.validated_data.get('provider')
        auto_execute = serializer.validated_data.get('auto_execute', False)
        
        # Get provider if specified
        provider = None
        if provider_id:
            provider = get_object_or_404(AIProvider, id=provider_id, is_active=True)
        
        # Create generation agent
        generation_agent = AIScriptGenerationAgent()
        
        # Generate script
        result = generation_agent.generate(prompt, provider)
        
        if not result['success']:
            return Response({
                'success': False,
                'message': 'Script generation failed',
                'error': result.get('error', 'Unknown error')
            }, status=status.HTTP_200_OK)  # Still return 200 as the API call succeeded
        
        # Get script object
        script_obj = result.get('script_obj')
        if not script_obj:
            # If running outside Django context or script_obj not returned,
            # create a Script model instance manually
            script_obj = Script.objects.create(
                prompt=prompt,
                content=result['script'],
                provider=provider,
                status='pending'
            )
        
        # Execute if requested
        if auto_execute:
            execution_agent = ManimExecutionAgent()
            exec_result = execution_agent.execute(script_obj)
            
            # Return combined result
            return Response({
                'success': True,
                'message': 'Script generated and executed',
                'script_id': str(script_obj.id),
                'execution_success': exec_result['success'],
                'output_path': exec_result.get('output_path'),
                'error': exec_result.get('error')
            }, status=status.HTTP_201_CREATED)
        
        # Return generation result
        return Response({
            'success': True,
            'message': 'Script generated successfully',
            'script_id': str(script_obj.id)
        }, status=status.HTTP_201_CREATED)


class ExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for script executions"""
    queryset = Execution.objects.all()
    serializer_class = ExecutionSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed execution"""
        execution = self.get_object()
        script = execution.script
        
        # Create execution agent
        execution_agent = ManimExecutionAgent()
        
        # Execute the script
        result = execution_agent.execute(script)
        
        # Return the result
        if result['success']:
            return Response({
                'success': True,
                'message': 'Execution retried successfully',
                'output_path': result['output_path'],
                'execution_id': result['execution'].id if 'execution' in result else None
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Execution retry failed',
                'error': result.get('error', 'Unknown error'),
                'execution_id': result['execution'].id if 'execution' in result else None
            }, status=status.HTTP_200_OK)


class AIProviderViewSet(viewsets.ModelViewSet):
    """API endpoint for AI providers"""
    queryset = AIProvider.objects.all()
    serializer_class = AIProviderSerializer
    permission_classes = [IsAuthenticated]


class ContainerViewSet(viewsets.ModelViewSet):
    """API endpoint for Docker containers"""
    queryset = Container.objects.all()
    serializer_class = ContainerSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def check_status(self, request, pk=None):
        """Check container status"""
        container = self.get_object()
        
        # Import here to avoid circular imports
        from .agents.docker_agent import DockerAgent
        
        # Create Docker agent and check status
        docker_agent = DockerAgent()
        is_running = docker_agent.check_container_status(container.name)
        
        # Update container record
        container.is_running = is_running
        container.save()
        
        return Response({
            'success': True,
            'is_running': is_running
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start container"""
        container = self.get_object()
        
        # Import here to avoid circular imports
        from .agents.docker_agent import DockerAgent
        
        # Create Docker agent and start container
        docker_agent = DockerAgent()
        result = docker_agent.ensure_container_running(container.name)
        
        # Update container record
        container.is_running = result
        container.save()
        
        return Response({
            'success': result,
            'is_running': container.is_running
        }, status=status.HTTP_200_OK)
