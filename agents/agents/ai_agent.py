import os
import traceback
import google.generativeai as genai
from openai import AzureOpenAI
from django.conf import settings
from .base_agent import BaseAgent

class AIScriptGenerationAgent(BaseAgent):
    """
    Agent responsible for generating animation scripts using AI providers.
    Supports multiple AI providers including Gemini and Azure OpenAI.
    """
    
    def __init__(self, debug=False):
        """Initialize the AI Script Generation Agent"""
        super().__init__(debug)
    
    def generate(self, prompt, provider=None):
        """
        Generate a Manim script using the specified AI provider
        
        Args:
            prompt (str): Description of the animation to create
            provider (str/AIProvider, optional): Provider to use or name/ID of a provider.
                                                If None, uses first available provider.
        
        Returns:
            dict: Result with script content, provider, and success flag
        """
        # Fetch provider if string was passed or use default
        provider_obj = self._get_provider(provider)
        
        if not provider_obj:
            error_msg = "No valid AI provider available for script generation"
            self.log_error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "script": None,
                "provider": None
            }
        
        # Craft a specialized prompt for animation generation
        manim_prompt = f"""
        Create a Manim animation script based on this description: "{prompt}"
        
        The script should:
        1. Import necessary Manim modules
        2. Define a Scene class 
        3. Implement the construct method with appropriate animations
        4. Use best practices for Manim code
        5. Include helpful comments explaining the animation steps
        
        VERY IMPORTANT: Return ONLY the raw Python code without any markdown formatting, code blocks, or explanation.
        DO NOT include ```python or ``` markers around the code. Just give me the pure Python code.
        """
        
        try:
            # Generate script using the appropriate provider
            provider_type = provider_obj.provider_type if hasattr(provider_obj, 'provider_type') else provider_obj
            
            if provider_type == 'gemini':
                script = self._generate_with_gemini(manim_prompt, provider_obj)
            elif provider_type == 'azure_openai':
                script = self._generate_with_azure_openai(manim_prompt, provider_obj)
            else:
                raise ValueError(f"Unsupported provider type: {provider_type}")
            
            
            # Create Script record in database if within Django context
            script_obj = self._create_script_record(prompt, script, provider_obj)
            
            return {
                "success": True,
                "script": script,
                "provider": provider_obj,
                "script_obj": script_obj
            }
            
        except Exception as e:
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            self.log_error(f"Error generating script: {error_msg}\n{stack_trace}")
            
            return {
                "success": False,
                "error": error_msg,
                "traceback": stack_trace,
                "script": None,
                "provider": provider_obj
            }
    
    def _generate_with_gemini(self, prompt, provider):
        """
        Generate script using Google's Gemini model
        
        Args:
            prompt (str): The prompt to send to Gemini
            provider (AIProvider/dict): The provider configuration
        
        Returns:
            str: Generated script text
        """
        # Get API key from provider or settings
        api_key = self._get_provider_credential(provider, 'api_key', settings.GEMINI_API_KEY)
        model_name = self._get_provider_credential(provider, 'model_name', 'gemini-2.5-flash-preview-04-17')
        
        if not api_key:
            raise ValueError("No Gemini API key available")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Call Gemini API
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        # Extract the text from the response
        if hasattr(response, 'text'):
            return response.text
        else:
            # Handle different response formats
            return str(response.candidates[0].content.parts[0].text)
    
    def _generate_with_azure_openai(self, prompt, provider):
        """
        Generate script using Azure OpenAI
        
        Args:
            prompt (str): The prompt to send to Azure OpenAI
            provider (AIProvider/dict): The provider configuration
        
        Returns:
            str: Generated script text
        """
        # Get credentials from provider or settings
        api_key = self._get_provider_credential(provider, 'api_key', settings.AZURE_OPENAI_API_KEY)
        endpoint = self._get_provider_credential(provider, 'endpoint', settings.AZURE_OPENAI_ENDPOINT)
        deployment = self._get_provider_credential(provider, 'deployment', settings.AZURE_OPENAI_DEPLOYMENT)
        
        if not api_key or not endpoint:
            raise ValueError("Azure OpenAI credentials not available")
        
        # Configure Azure OpenAI client
        client = AzureOpenAI(
            api_key=api_key,
            api_version="2023-07-01-preview",
            azure_endpoint=endpoint
        )
        
        # Call Azure OpenAI API
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are an expert Manim developer who creates beautiful animations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    
    
    def _get_provider(self, provider=None):
        """
        Get the provider object to use for generation
        
        Args:
            provider (str/AIProvider, optional): Provider to use or identifier. 
                                                If None, uses first active provider.
        
        Returns:
            AIProvider/str: Provider object or name
        """
        # If provider is already specified and not a string, use it directly
        if provider and not isinstance(provider, str):
            return provider
            
        try:
            # Try to import AIProvider model - handle circular imports
            from ..models import AIProvider as AIProviderModel
            
            # If provider is a string (name or ID), look it up
            if provider and isinstance(provider, str):
                # Try as name
                provider_obj = AIProviderModel.objects.filter(name=provider, is_active=True).first()
                if not provider_obj:
                    # Try as ID
                    provider_obj = AIProviderModel.objects.filter(id=provider, is_active=True).first()
                return provider_obj
            
            # Use first active provider by priority
            return AIProviderModel.objects.filter(is_active=True).order_by('priority').first()
            
        except Exception:
            # If we can't access the database or running outside Django context
            # Use the provider string or default to settings-based provider
            if provider and isinstance(provider, str):
                return provider
                
            # Check available providers in settings
            if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
                return 'gemini'
            elif (hasattr(settings, 'AZURE_OPENAI_API_KEY') and settings.AZURE_OPENAI_API_KEY and
                  hasattr(settings, 'AZURE_OPENAI_ENDPOINT') and settings.AZURE_OPENAI_ENDPOINT):
                return 'azure_openai'
            
            return None
    
    def _get_provider_credential(self, provider, credential_name, default=None):
        """
        Get a credential from provider object or return default
        
        Args:
            provider (AIProvider/str): The provider object or name
            credential_name (str): Name of the credential to retrieve
            default (any, optional): Default value if credential not found
            
        Returns:
            any: The credential value or default
        """
        # If provider is a database object
        if hasattr(provider, credential_name):
            return getattr(provider, credential_name)
            
        # Otherwise use the default
        return default
    
    def _create_script_record(self, prompt, script_content, provider):
        """
        Create a database record for the generated script
        
        Args:
            prompt (str): The original prompt
            script_content (str): The generated script
            provider (AIProvider/str): The provider used
            
        Returns:
            Script: The created Script object or None if outside Django context
        """
        try:
            # Try to import Script model - handle circular imports
            from ..models import Script, AIProvider
            
            # Find the scene class name
            scene_class = None
            for line in script_content.split('\n'):
                if line.strip().startswith('class ') and '(Scene)' in line:
                    scene_class = line.strip().split('class ')[1].split('(')[0].strip()
                    break
            
            # If provider is a string, try to find the provider object
            provider_obj = provider
            if isinstance(provider, str):
                provider_obj = AIProvider.objects.filter(
                    provider_type=provider, is_active=True
                ).order_by('priority').first()
            
            # Create the script record
            script_obj = Script.objects.create(
                prompt=prompt,
                content=script_content,
                scene_class=scene_class,
                provider=provider_obj if not isinstance(provider_obj, str) else None,
                status='pending'
            )
            
            return script_obj
            
        except Exception as e:
            # This is expected during early setup when database might not be ready
            # or when running outside of Django context
            self.log_debug(f"Could not create script record: {str(e)}")
            return None


class AIScriptDebuggingAgent(BaseAgent):
    """
    Agent responsible for debugging and fixing Manim scripts using AI.
    """
    
    def __init__(self, debug=False):
        """Initialize the AI Script Debugging Agent"""
        super().__init__(debug)
        self.script_generator = AIScriptGenerationAgent(debug)
    
    def debug(self, script, error_message, provider=None, execution=None):
        """
        Debug a Manim script that encountered an error using AI
        
        Args:
            script (str): The script content to debug
            error_message (str): The error message from execution
            provider (str/AIProvider, optional): Provider to use for debugging
            execution (Execution, optional): The execution record for tracking
            
        Returns:
            dict: Result with fixed script and success flag
        """
        # Get provider to use
        provider_obj = self.script_generator._get_provider(provider)
        
        if not provider_obj:
            error_msg = "No valid AI provider available for script debugging"
            self.log_error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "fixed_script": None
            }
        
        # Create debug prompt
        debug_prompt = f"""
        I'm trying to run a Manim animation script, but it's throwing the following error:
        
        {error_message}
        
        Here's the script:
        
        ```python
        {script}
        ```
        
        Please fix this script to resolve the error. Return ONLY the corrected Python code without any markdown formatting, code blocks, or explanation.
        DO NOT include ```python or ``` markers around the code. Just give me the pure Python code.
        """
        
        try:
            # Update execution record if provided
            if execution:
                self._update_execution(execution, "debugging", script)
            
            # Generate fixed script
            provider_type = provider_obj.provider_type if hasattr(provider_obj, 'provider_type') else provider_obj
            
            if provider_type == 'gemini':
                fixed_script = self._debug_with_gemini(debug_prompt, provider_obj)
            elif provider_type == 'azure_openai':
                fixed_script = self._debug_with_azure_openai(debug_prompt, provider_obj)
            else:
                raise ValueError(f"Unsupported provider type: {provider_type}")
            
            # Clean up the fixed script
            cleaned_script = self.script_generator._clean_script(fixed_script)
            
            # Update execution record if provided
            if execution:
                self._update_execution(execution, "pending", script, cleaned_script)
            
            return {
                "success": True,
                "fixed_script": cleaned_script,
                "changed": cleaned_script != script
            }
            
        except Exception as e:
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            self.log_error(f"Error debugging script: {error_msg}\n{stack_trace}")
            
            # Try basic correction if AI debugging fails
            fixed_script = self._basic_correction(script, error_message)
            changed = fixed_script != script
            
            # Update execution record if provided
            if execution and changed:
                self._update_execution(execution, "pending", script, fixed_script)
            
            return {
                "success": changed,
                "error": error_msg,
                "fixed_script": fixed_script,
                "changed": changed
            }
    
    def _debug_with_gemini(self, prompt, provider):
        """Use Gemini to debug the script"""
        return self.script_generator._generate_with_gemini(prompt, provider)
    
    def _debug_with_azure_openai(self, prompt, provider):
        """Use Azure OpenAI to debug the script"""
        return self.script_generator._generate_with_azure_openai(prompt, provider)
    
    def _basic_correction(self, script, error_message):
        """
        Attempt some basic corrections based on common Manim errors
        
        Args:
            script (str): Original script content
            error_message (str): Error message from execution
            
        Returns:
            str: Corrected script or original if no corrections possible
        """
        self.log_warning("AI debugging failed, using simple correction strategy")
        
        # If manim not recognized, it's likely just an execution environment issue
        if "'manim' is not recognized" in error_message:
            return script
        
        # Import error correction
        if "No module named" in error_message:
            # Try to extract the module name and suggest an import
            try:
                module_name = error_message.split("No module named")[1].strip().strip("'").strip('"')
                if module_name:
                    return f"import {module_name}\n\n{script}"
            except Exception:
                pass
        
        # Property or method not found
        if "has no attribute" in error_message:
            # This is harder to fix automatically
            pass
        
        # Return original if no fixes applied
        return script
    
    def _update_execution(self, execution, status, original_script=None, modified_script=None):
        """
        Update the execution record with debugging information
        
        Args:
            execution (Execution): The execution record to update
            status (str): New status for the script
            original_script (str, optional): Original script if not already set
            modified_script (str, optional): Modified script from debugging
            
        Returns:
            Execution: Updated execution record
        """
        try:
            # Set original script if not already set
            if original_script and not execution.original_script:
                execution.original_script = original_script
            
            # Set modified script if provided
            if modified_script:
                execution.modified_script = modified_script
            
            # Update script status
            if hasattr(execution, 'script') and execution.script:
                execution.script.status = status
                execution.script.save()
            
            # Save execution
            execution.save()
            
            return execution
        except Exception as e:
            self.log_error(f"Error updating execution record: {str(e)}")
            return execution 