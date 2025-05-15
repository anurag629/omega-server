import logging
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.views.generic import TemplateView
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
import traceback
from datetime import datetime
from .models import ManimScript
from .serializers import ManimScriptSerializer, ManimScriptGenerateSerializer
from .services import generate_manim_script, execute_manim_script

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    # Only show page that service is up and running without any template 
    def get(self, request, *args, **kwargs):
        return HttpResponse("Omega service is up and running. Current time: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class ManimScriptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Manim scripts
    """
    queryset = ManimScript.objects.all()
    serializer_class = ManimScriptSerializer
    permission_classes = [IsAuthenticated]  # Temporarily remove IsApprovedAndVerifiedUser
    
    def get_queryset(self):
        """Filter scripts to only show those created by the current user"""
        if self.request.user.is_staff:
            return ManimScript.objects.all()
        return ManimScript.objects.filter(user=self.request.user)


class GenerateManimScriptAPIView(APIView):
    """
    API endpoint to generate Manim scripts
    """
    permission_classes = [IsAuthenticated]  # Temporarily remove IsApprovedAndVerifiedUser
    
    def post(self, request, *args, **kwargs):
        serializer = ManimScriptGenerateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        prompt = serializer.validated_data['prompt']
        provider = serializer.validated_data['provider']
        should_execute = serializer.validated_data.get('execute', False)
        
        try:
            # Generate the script
            script = generate_manim_script(prompt, provider)
            
            # Create ManimScript object
            manim_script = ManimScript.objects.create(
                prompt=prompt,
                script=script,
                provider=provider,
                status='pending',
                user=request.user  # Associate with the current user
            )
            
            response_data = {
                'id': str(manim_script.id),  # Convert UUID to string
                'script': script
            }
            
            # Execute the script if requested
            if should_execute:
                try:
                    result = execute_manim_script(script)
                    
                    # Update the model with execution results
                    script_path = result['script_path']
                    output_path = result['output_path']
                    output_url = f"{settings.BASE_URL}/media/{output_path}"
                    
                    manim_script.script_path = script_path
                    manim_script.output_path = output_path
                    manim_script.output_url = output_url
                    manim_script.status = 'completed'
                    manim_script.save()
                    
                    # Add execution data to response
                    response_data['script_path'] = script_path
                    response_data['output_path'] = output_path
                    response_data['output_url'] = output_url
                    
                except Exception as e:
                    error_msg = str(e)
                    stack_trace = traceback.format_exc()
                    logger.error(f"Error executing script: {error_msg}\n{stack_trace}")
                    
                    manim_script.status = 'failed'
                    manim_script.error_message = error_msg
                    manim_script.save()
                    
                    response_data['error'] = error_msg
            
            # Log the response data for debugging
            logger.info(f"API Response data: {response_data}")
            
            return Response(response_data)
            
        except Exception as e:
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            logger.error(f"Error in generate_manim API: {error_msg}\n{stack_trace}")
            return Response({
                'error': error_msg
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def serve_media(request, path):
    """
    Serve media files
    """
    import os
    from django.http import Http404
    
    # Construct path to the media file
    media_root = settings.MEDIA_ROOT
    file_path = os.path.join(media_root, path)
    
    if not os.path.exists(file_path):
        logger.error(f"Media file not found: {file_path}")
        raise Http404(f"File not found: {path}")
    
    try:
        return FileResponse(open(file_path, 'rb'))
    except Exception as e:
        logger.error(f"Error serving file {file_path}: {str(e)}")
        raise Http404(f"Error accessing file: {path}") 