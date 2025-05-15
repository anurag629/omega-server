import os
import uuid
import logging
import requests
import traceback
import subprocess
import google.generativeai as genai
from openai import AzureOpenAI
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_manim_script(prompt, provider):
    """
    Generate a Manim script using the specified AI provider
    """
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
    
    script = None
    
    if provider == 'gemini':
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
            
        # Call Gemini API
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(manim_prompt)
        
        # Extract the text from the response
        if hasattr(response, 'text'):
            script = response.text
        else:
            # Handle different response formats
            script = str(response.candidates[0].content.parts[0].text)
            
    elif provider == 'azure_openai':
        if not settings.AZURE_OPENAI_API_KEY or not settings.AZURE_OPENAI_ENDPOINT:
            raise ValueError("Azure OpenAI credentials not set in environment variables")
            
        # Configure Azure OpenAI client
        client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version="2023-07-01-preview",
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        
        # Call Azure OpenAI API
        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are an expert Manim developer who creates beautiful animations."},
                {"role": "user", "content": manim_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        script = response.choices[0].message.content
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'gemini' or 'azure_openai'")
        
    # Clean up the script - remove any markdown formatting
    return clean_script(script)


def clean_script(script):
    """
    Clean up AI-generated script to ensure it's valid Python
    """
    # Remove markdown code blocks
    cleaned = script.replace('```python', '').replace('```', '')
    
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # Check if the script starts with proper imports
    if not cleaned.startswith('from manim import') and not cleaned.startswith('import manim'):
        # Add a basic import if needed
        cleaned = 'from manim import *\n\n' + cleaned
    
    # Ensure the script has correct Scene class
    has_scene_class = False
    for line in cleaned.split('\n'):
        if 'class' in line and 'Scene' in line:
            has_scene_class = True
            break
    
    if not has_scene_class:
        # Add a basic Scene class skeleton
        logger.warning("No scene class found in generated script, adding a basic one")
        cleaned += "\n\nclass DefaultScene(Scene):\n    def construct(self):\n        self.add(Text('Generated animation'))\n"
    
    return cleaned


def debug_manim_script(script, error_message):
    """
    Debug a Manim script that encountered an error using AI
    """
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
        if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
            # Use Azure OpenAI for debugging
            # Make sure we don't pass any proxy settings which may cause issues with newer OpenAI client versions
            # Save the current proxy settings
            http_proxy = os.environ.pop('HTTP_PROXY', None)
            https_proxy = os.environ.pop('HTTPS_PROXY', None)
            
            try:
                client = AzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version="2023-07-01-preview",
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
                )
                
                response = client.chat.completions.create(
                    model=settings.AZURE_OPENAI_DEPLOYMENT,
                    messages=[
                        {"role": "system", "content": "You are an expert Manim developer who can fix errors in animation scripts."},
                        {"role": "user", "content": debug_prompt}
                    ],
                    temperature=0.3,  # Lower temperature for more precise fixes
                    max_tokens=4000
                )
                
                fixed_script = response.choices[0].message.content
            finally:
                # Restore proxy settings
                if http_proxy:
                    os.environ['HTTP_PROXY'] = http_proxy
                if https_proxy:
                    os.environ['HTTPS_PROXY'] = https_proxy
        elif settings.GEMINI_API_KEY:
            # Fallback to Gemini if Azure OpenAI is not configured
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(debug_prompt)
            
            if hasattr(response, 'text'):
                fixed_script = response.text
            else:
                fixed_script = str(response.candidates[0].content.parts[0].text)
        else:
            raise ValueError("No AI provider configured for debugging")
            
        # Clean up the fixed script
        return clean_script(fixed_script)
    except Exception as e:
        logger.error(f"Error debugging Manim script: {str(e)}")
        raise ValueError(f"Failed to debug script: {str(e)}")


def install_missing_dependencies(error_message):
    """
    Attempt to install missing dependencies in the Manim container
    """
    # Check for common import error patterns
    if "No module named" in error_message or "ImportError" in error_message:
        # Extract module name from error message
        import_lines = [line for line in error_message.split('\n') if "No module named" in line or "ImportError" in line]
        if import_lines:
            module_line = import_lines[0]
            # Extract module name (this is a simple heuristic, might need refinement)
            if "No module named" in module_line:
                module_name = module_line.split("No module named")[1].strip().strip("'").strip('"')
            else:
                module_name = module_line.split("ImportError:")[1].strip().split(" ")[0].strip("'").strip('"')
            
            logger.info(f"Attempting to install missing module: {module_name}")
            
            try:
                # Execute the installation script in the container
                container_name = "omega-manim"
                install_command = f"pip install {module_name}"
                subprocess.run(
                    ["docker", "exec", container_name, "bash", "-c", install_command],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info(f"Successfully installed {module_name} in container")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {module_name}: {e.stderr}")
                return False
    return False


def execute_manim_script(script, script_id=None):
    """
    Executes the generated Manim script in the Manim container
    with automatic error handling and debugging
    """
    # If no script_id is provided, generate a unique ID
    if script_id is None:
        script_id = str(uuid.uuid4())
    
    # Maximum number of debug attempts
    max_debug_attempts = 3
    current_attempt = 0
    current_script = script
    
    while current_attempt < max_debug_attempts:
        current_attempt += 1
        
        logger.info(f"Executing script with ID {script_id} (attempt {current_attempt})")
        
        try:
            # Get the scene class name from the script
            scene_class = None
            for line in current_script.split('\n'):
                if line.strip().startswith('class ') and '(Scene)' in line:
                    scene_class = line.strip().split('class ')[1].split('(')[0].strip()
                    break
                    
            if not scene_class:
                raise ValueError("Could not find a Scene class in the generated script")
            
            logger.info(f"Using scene class: {scene_class}")
            
            # Send a request to the Manim container
            manim_url = f"http://{settings.MANIM_SERVICE}:{settings.MANIM_SERVICE_PORT}/execute-manim"
            logger.info(f"Sending request to Manim service at {manim_url}")
            
            try:
                response = requests.post(
                    manim_url,
                    json={
                        'script_content': current_script,
                        'scene_class': scene_class,
                        'script_id': str(script_id)
                    },
                    timeout=300  # Increased timeout for complex animations
                )
                
                logger.info(f"Manim container response status: {response.status_code}")
                
                if not response.ok:
                    logger.error(f"Manim execution failed with status {response.status_code}: {response.text}")
                    raise ValueError(f"Manim execution failed: {response.text}")
                
                try:
                    response_data = response.json()
                    logger.info(f"Manim response data: {response_data}")
                    
                    if not response_data.get('success'):
                        error_msg = response_data.get('error', 'Unknown error')
                        logger.error(f"Manim execution failed: {error_msg}")
                        
                        # Check if this is the last attempt
                        if current_attempt >= max_debug_attempts:
                            raise ValueError(f"Max debug attempts reached. Last error: {error_msg}")
                        
                        # Try to install missing dependencies if error suggests that's the issue
                        if install_missing_dependencies(error_msg):
                            logger.info("Installed missing dependencies, retrying script execution")
                            continue
                        
                        # Debug the script with AI
                        logger.info("Attempting to debug script with AI")
                        current_script = debug_manim_script(current_script, error_msg)
                        logger.info("AI provided a fixed script, will retry execution")
                        continue  # Retry with fixed script
                    
                    # Get the output path from the response
                    output_path = response_data.get('output_path')
                    if not output_path:
                        raise ValueError("Missing output_path in Manim response")
                    
                    # Return script and output path
                    result = {
                        'script': current_script,
                        'output_path': output_path
                    }
                    logger.info(f"Manim execution successful. Result: {result}")
                    return result
                    
                except ValueError as ve:
                    # Re-raise ValueError for specific error handling
                    raise ve
                    
                except Exception as je:
                    # Handle JSON parsing errors
                    logger.error(f"Error parsing JSON response: {str(je)}\nResponse content: {response.text}")
                    raise ValueError(f"Failed to parse Manim service response: {str(je)}")
                    
            except requests.RequestException as re:
                # Check if connection refused (container not running)
                if "connection" in str(re).lower() and "refused" in str(re).lower():
                    logger.error(f"Connection to Manim service refused. Make sure the container is running.")
                    raise ValueError(f"Failed to connect to Manim service: {str(re)}")
                # Handle other request errors (timeouts, etc.)
                logger.error(f"Request to Manim service failed: {str(re)}")
                raise ValueError(f"Failed to communicate with Manim service: {str(re)}")
            
        except ValueError as ve:
            # If this is the last attempt, raise the error
            if current_attempt >= max_debug_attempts:
                raise ve
            
            # Extract error message for debugging
            error_msg = str(ve)
            
            # Try to install missing dependencies if error suggests that's the issue
            if install_missing_dependencies(error_msg):
                logger.info("Installed missing dependencies, retrying script execution")
                continue
            
            # Debug the script with AI
            logger.info("Attempting to debug script with AI")
            try:
                current_script = debug_manim_script(current_script, error_msg)
                logger.info("AI provided a fixed script, will retry execution")
            except Exception as debug_error:
                logger.error(f"Failed to debug script: {str(debug_error)}")
                raise ValueError(f"Failed to generate or debug Manim script after {current_attempt} attempts. Last error: {error_msg}")
        
        except Exception as e:
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            logger.error(f"Error executing Manim script: {error_msg}\n{stack_trace}")
            
            # If this is the last attempt, raise the error
            if current_attempt >= max_debug_attempts:
                raise
            
            # Try to install missing dependencies if error suggests that's the issue
            if install_missing_dependencies(error_msg):
                logger.info("Installed missing dependencies, retrying script execution")
                continue
            
            # Debug the script with AI
            logger.info("Attempting to debug script with AI")
            try:
                current_script = debug_manim_script(current_script, error_msg)
                logger.info("AI provided a fixed script, will retry execution")
            except Exception as debug_error:
                logger.error(f"Failed to debug script: {str(debug_error)}")
                raise ValueError(f"Failed to generate or debug Manim script after {current_attempt} attempts. Last error: {error_msg}")
    
    # If we get here, we've exhausted all attempts
    raise ValueError(f"Failed to generate or debug Manim script after {max_debug_attempts} attempts") 