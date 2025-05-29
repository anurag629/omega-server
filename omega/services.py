import os
import uuid
import requests
import traceback
import subprocess
import tempfile
import google.generativeai as genai
from openai import AzureOpenAI
from django.conf import settings


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
        model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
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
    return script


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
    
    # Try using Gemini first as it's less likely to have proxy issues
    if settings.GEMINI_API_KEY:
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
            response = model.generate_content(debug_prompt)
            
            if hasattr(response, 'text'):
                fixed_script = response.text
            else:
                fixed_script = str(response.candidates[0].content.parts[0].text)
                
            # Clean up the fixed script
            return clean_script(fixed_script)
        except Exception as gemini_error:
            # Continue to try Azure OpenAI if Gemini fails
            pass
    
    # Only try Azure OpenAI if configured and Gemini failed or isn't configured
    if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
        try:
            # Create client with minimal configuration to avoid proxy issues
            # Using a fresh import in a separate function to isolate potential issues
            fixed_script = _azure_openai_debug(debug_prompt)
            
            if fixed_script:
                return clean_script(fixed_script)
            else:
                raise ValueError("Azure OpenAI returned empty response")
        except Exception as azure_error:
            # If both methods fail, fall back to a simple correction strategy
            pass
    
    # If both AI services fail, try a simple correction approach
    
    # Attempt some basic corrections based on common Manim errors
    if "'manim' is not recognized" in error_message:
        # This is likely just an execution environment issue, return the script as is
        return script
    
    if "No module named" in error_message:
        # Try to extract the module name and suggest an import
        module_name = error_message.split("No module named")[1].strip().strip("'").strip('"')
        if module_name:
            return f"import {module_name}\n\n{script}"
    
    # If we can't fix it, return the original script
    return script


def _azure_openai_debug(prompt):
    """
    Isolated function to handle Azure OpenAI API calls to avoid proxy issues
    """
    try:
        # Fresh import to avoid any cached configuration issues
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY, 
            api_version="2023-07-01-preview",
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        
        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are an expert Manim developer who can fix errors in animation scripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return None


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
            
            try:
                # Execute the installation script in the container
                container_name = "omega-manim"
                install_command = f"pip install {module_name}"
                subprocess.run(
                    ["docker", "exec", container_name, "bash", "-c", install_command],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )
                return True
            except subprocess.CalledProcessError as e:
                return False
    return False


def ensure_docker_container_running(container_name="omega-manim"):
    """
    Check if the Docker container is running and start it if needed
    """
    try:
        # Check if container exists and is running
        check_cmd = ["docker", "container", "inspect", "-f", "{{.State.Running}}", container_name]
        result = subprocess.run(check_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        
        if result.returncode != 0:
            return False
            
        if result.stdout.strip() == "true":
            return True
            
        # If container exists but is not running, start it
        start_cmd = ["docker", "start", container_name]
        start_result = subprocess.run(start_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        
        if start_result.returncode == 0:
            return True
        else:
            return False
            
    except Exception as e:
        return False


def execute_manim_locally(script_content, scene_class, script_id):
    """
    Execute Manim script directly from memory without saving to a permanent file
    """
    
    # Check and ensure Docker container is running first
    container_name = "omega-manim"
    docker_available = ensure_docker_container_running(container_name)
    
    # Create a unique identifier for this execution
    base_name = f"manim_script_{script_id}"
    media_root = settings.MEDIA_ROOT
    
    # Create temp file for output capture
    with tempfile.NamedTemporaryFile(prefix="manim_output_", suffix=".txt", delete=False, mode="w+", encoding="utf-8") as output_file:
        output_file_path = output_file.name
    
    # Create a temporary script file
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w+", encoding="utf-8") as script_file:
        # Write the script content to the temp file
        script_file.write(script_content)
        script_path = script_file.name
    
    try:
        # Clean script if needed - working directly with the temp file
        clean_script_content(script_path)
        
        # Prepare the command - adjust based on your environment
        container_name = "omega-manim"
        
        if settings.MANIM_SERVICE == "localhost":
            # Local development - for local execution, check if Docker is available first
            # since Manim might not be installed in the local environment
            try:
                # Try to use Docker even in local development mode
                docker_run_cmd = [
                    "docker", "exec", container_name, 
                    "bash", "-c", f"cd /manim && python -m manim {os.path.basename(script_path)} {scene_class} -qm"
                ]
                
                # Copy the script to container first
                temp_container_path = f"/tmp/{os.path.basename(script_path)}"
                copy_cmd = ["docker", "cp", script_path, f"{container_name}:{temp_container_path}"]
                subprocess.run(copy_cmd, check=True, capture_output=True, encoding="utf-8", errors="replace")
                
                # Move the script to the manim directory in the container
                mv_cmd = ["docker", "exec", container_name, "bash", "-c", f"cp {temp_container_path} /manim/{os.path.basename(script_path)}"]
                subprocess.run(mv_cmd, check=True, capture_output=True, encoding="utf-8", errors="replace")
                
                # Execute manim in the container
                process = subprocess.run(docker_run_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
                complete_output = process.stdout + process.stderr
            except Exception as e:
                # If Docker execution fails, try direct command as before
                cmd = f"cd {media_root} && manim {script_path} {scene_class} -qm 2>&1"
                process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                complete_output = process.stdout + process.stderr
        else:
            # Use Docker container - copy temp file into container first
            temp_container_path = f"/tmp/{os.path.basename(script_path)}"
            
            # Copy the script to the container
            copy_cmd = ["docker", "cp", script_path, f"{container_name}:{temp_container_path}"]
            subprocess.run(copy_cmd, check=True, capture_output=True, encoding="utf-8", errors="replace")
            
            # Move the script to the manim directory in the container
            mv_cmd = ["docker", "exec", container_name, "bash", "-c", f"cp {temp_container_path} /manim/{os.path.basename(script_path)}"]
            subprocess.run(mv_cmd, check=True, capture_output=True, encoding="utf-8", errors="replace")
            
            # Remove the temporary file from Docker container
            rm_cmd = ["docker", "exec", container_name, "bash", "-c", f"rm -f {temp_container_path}"]
            subprocess.run(rm_cmd, capture_output=True, encoding="utf-8", errors="replace")
            
            # Execute manim in the container - using python -m manim for better reliability
            cmd = f"cd /manim && python -m manim {os.path.basename(script_path)} {scene_class} -qm"
            process = subprocess.run(
                ["docker", "exec", container_name, "bash", "-c", cmd],
                capture_output=True,
                text=True,
                encoding="utf-8", 
                errors="replace"
            )
            complete_output = process.stdout + process.stderr
            
            # Clean up script file in Docker container after execution
            cleanup_cmd = f"rm -f /manim/{os.path.basename(script_path)}"
            subprocess.run(
                ["docker", "exec", container_name, "bash", "-c", cleanup_cmd],
                capture_output=True,
                encoding="utf-8",
                errors="replace"
            )
        
        # Write the output to file for reference with proper encoding
        with open(output_file_path, "w", encoding="utf-8", errors="replace") as f:
            f.write(complete_output)
        
        # Determine the expected output path
        # Note: Manim creates output dirs based on the script filename without path
        script_basename = os.path.basename(script_path).replace('.py', '')
        output_path = f"videos/{script_basename}/720p30/{scene_class}.mp4"
        full_output_path = os.path.join(media_root, output_path)
        
        # Check if output file exists in the expected location
        success = process.returncode == 0
        
        # If process was successful but file doesn't exist in the expected path,
        # try to find it in the media directory
        if success and not os.path.exists(full_output_path):
            media_dir = os.path.join(media_root, f"videos/{script_basename}/720p30/")
            if os.path.exists(media_dir):
                files = os.listdir(media_dir)
                if files:  # Use first file if any exist
                    output_path = f"videos/{script_basename}/720p30/{files[0]}"
                    full_output_path = os.path.join(media_root, output_path)
        
        # Final check if the file exists
        if os.path.exists(full_output_path):
            result = {
                "success": True,
                "output": complete_output,
                "output_path": output_path
            }
        else:
            # Extract error information
            error_info = complete_output
            if "TypeError: " in complete_output:
                # Extract TypeError and related lines for improved debugging
                error_lines = []
                for line in complete_output.split("\n"):
                    if "TypeError: " in line or "❱" in line:
                        error_lines.append(line)
                    # Also capture stack frames for context
                    if ".py" in line and "in" in line:
                        error_lines.append(line)
                if error_lines:
                    error_info = "\n".join(error_lines)
            
            result = {
                "success": False,
                "error": error_info,
                "output": complete_output
            }
        
        return result
    except Exception as e:
        error_msg = str(e)
        stack_trace = traceback.format_exc()
        return {
            "success": False,
            "error": f"{error_msg}\n{stack_trace}",
            "output": ""
        }
    finally:
        # Clean up temporary files
        try:
            # Delete the primary temp files we created
            if os.path.exists(script_path):
                os.unlink(script_path)
            if os.path.exists(output_file_path):
                os.unlink(output_file_path)
                
            # Clean up any temp directories created by Docker/Manim
            script_basename = os.path.basename(script_path).replace('.py', '')
            
            # Get the server root directory (one level up from media_root)
            server_root = os.path.dirname(media_root)
            
            temp_dirs = [
                os.path.join(tempfile.gettempdir(), f"tmp{script_basename}*"),
                os.path.join(tempfile.gettempdir(), f"manim_*_{script_id}*"),
                os.path.join(media_root, f"videos/tmp{script_basename}*"),
                # Add patterns for direct omega-server temp files
                os.path.join(server_root, "tmp*.py"),
                os.path.join(server_root, "tmp*"),
                # Add specific pattern for the temp file the user mentioned
                os.path.join(server_root, "tmp*fwni.py"),
                os.path.join(server_root, "tmp*fwni")
            ]
            
            # Use glob to find and remove matching temp dirs
            import glob
            import shutil
            for pattern in temp_dirs:
                for temp_dir in glob.glob(pattern):
                    if os.path.isdir(temp_dir):
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    elif os.path.isfile(temp_dir):
                        os.unlink(temp_dir)
        except Exception as e:
            pass


def clean_script_content(script_path):
    """Clean script content in the temporary file if needed"""
    try:
        with open(script_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        if "```python" in content or "```" in content:
            cleaned_content = content.replace("```python", "").replace("```", "").strip()
            
            with open(script_path, "w", encoding="utf-8", errors="replace") as f:
                f.write(cleaned_content)
        
        # Clean up any other temp files that may have been created in the root directory
        try:
            server_root = os.path.dirname(settings.MEDIA_ROOT)
            import glob
            
            # Check for temp files in the server root with similar names
            basename = os.path.basename(script_path)
            if basename.startswith('tmp'):
                # Look for similar temp files
                similar_pattern = os.path.join(server_root, basename[:5] + '*')
                for similar_file in glob.glob(similar_pattern):
                    if similar_file != script_path and os.path.isfile(similar_file):
                        os.unlink(similar_file)
        except Exception as cleanup_err:
            pass
            
        return True
    except Exception as e:
        return False


def execute_manim_script(script, script_id=None):
    """
    Executes the generated Manim script directly from memory
    with automatic error handling and debugging
    """
    # If no script_id is provided, generate a unique ID
    if script_id is None:
        script_id = str(uuid.uuid4())
    
    # Maximum number of debug attempts
    max_debug_attempts = 3
    current_attempt = 0
    current_script = script
    last_error = None
    
    while current_attempt < max_debug_attempts:
        current_attempt += 1
        
        try:
            # Get the scene class name from the script
            scene_class = None
            for line in current_script.split('\n'):
                if line.strip().startswith('class ') and '(Scene)' in line:
                    scene_class = line.strip().split('class ')[1].split('(')[0].strip()
                    break
                    
            if not scene_class:
                raise ValueError("Could not find a Scene class in the generated script")
            
            # Execute Manim directly with script content
            result = execute_manim_locally(current_script, scene_class, script_id)
            
            if not result.get('success'):
                error_msg = result.get('error', 'Unknown error')
                last_error = error_msg
                
                # Check if this is the last attempt
                if current_attempt >= max_debug_attempts:
                    # Return a partial result with the current script and error
                    return {
                        'script': current_script,
                        'output_path': None,
                        'error': error_msg,
                        'success': False
                    }
                
                # Try to install missing dependencies if error suggests that's the issue
                if install_missing_dependencies(error_msg):
                    continue
                
                # Debug the script with AI
                try:
                    fixed_script = debug_manim_script(current_script, error_msg)
                    if fixed_script != current_script:
                        current_script = fixed_script
                        continue  # Retry with fixed script
                    else:
                        pass
                except Exception as debug_error:
                    # Continue with the original script, don't give up
                    pass
            
            # Get the output path from the result
            output_path = result.get('output_path')
            if not output_path:
                raise ValueError("Missing output_path in Manim execution result")
            
            # Return script and output path
            return {
                'script': current_script,
                'output_path': output_path,
                'success': True
            }
            
        except ValueError as ve:
            error_msg = str(ve)
            last_error = error_msg
            
            # If this is the last attempt, return a partial result
            if current_attempt >= max_debug_attempts:
                return {
                    'script': current_script,
                    'output_path': None,
                    'error': error_msg,
                    'success': False
                }
            
            # Try again with a slightly modified script or parameter
            if "Could not find a Scene class" in error_msg:
                # Add a basic scene class and retry
                current_script += "\n\nclass DefaultScene(Scene):\n    def construct(self):\n        self.add(Text('Generated animation'))\n"
                continue
        
        except Exception as e:
            error_msg = str(e)
            last_error = error_msg
            stack_trace = traceback.format_exc()
            
            # If this is the last attempt, return a partial result
            if current_attempt >= max_debug_attempts:
                return {
                    'script': current_script,
                    'output_path': None,
                    'error': error_msg,
                    'success': False
                }
    
    # If we get here, we've exhausted all attempts but want to return something
    result = {
        'script': current_script,
        'output_path': None,
        'error': last_error or "Failed to generate or debug Manim script after multiple attempts",
        'success': False
    }
    
    # Final failsafe cleanup for temp files matching Manim patterns
    try:
        import glob
        import shutil
        server_root = os.path.dirname(settings.MEDIA_ROOT)
        
        # Comprehensive temp file patterns
        patterns = [
            os.path.join(server_root, "tmp*.py"),
            os.path.join(server_root, "tmp*"),
            os.path.join(server_root, "*.py.tmp*"),
            os.path.join(tempfile.gettempdir(), "tmp*manim*"),
            os.path.join(tempfile.gettempdir(), "manim_*")
        ]
        
        # Find and remove all matching files and directories
        for pattern in patterns:
            for path in glob.glob(pattern):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        os.unlink(path)
                except Exception as e:
                    pass
    except Exception as cleanup_error:
        pass
        
    return result