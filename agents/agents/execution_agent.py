import os
import re
import uuid
import glob
import shutil
import tempfile
import traceback
from django.conf import settings
from django.utils import timezone
from .base_agent import BaseAgent
from .docker_agent import DockerAgent
from .dependency_agent import DependencyAgent
from .ai_agent import AIScriptDebuggingAgent

class ManimExecutionAgent(BaseAgent):
    """
    Agent responsible for executing Manim scripts and handling the execution process.
    Manages temporary files, Docker execution, and results tracking.
    """
    
    def __init__(self, debug=False):
        """Initialize the Manim Execution Agent"""
        super().__init__(debug)
        self.docker_agent = DockerAgent(debug)
        self.dependency_agent = DependencyAgent(debug)
        self.debug_agent = AIScriptDebuggingAgent(debug)
        
        # Container name - can be overridden in configuration
        self.container_name = getattr(settings, 'MANIM_CONTAINER_NAME', 'omega-manim')
        
        # Container working directory
        self.working_dir = getattr(settings, 'MANIM_WORKING_DIR', '/manim')
        
        # Output media directory
        self.media_root = settings.MEDIA_ROOT
    
    def execute(self, script, max_attempts=100):
        """
        Execute a Manim script
        
        Args:
            script (Script/str/dict): The script to execute - can be:
                - Script model object
                - String with script content
                - Dict with script content and other properties
            max_attempts (int, optional): Maximum number of execution attempts. Defaults to 100.
            
        Returns:
            dict: Result with execution status, output path, and details
        """
        # Extract script content and ID based on input type
        script_id, script_content, script_obj = self._prepare_script(script)
        
        # Create a new execution record if script_obj is available
        execution_id = str(uuid.uuid4())
        execution_obj = self._create_execution_record(script_obj, execution_id)
        
        # Execute with retry logic
        attempt = 0
        last_error = None
        current_script = script_content
        
        # Track timing
        start_time = timezone.now()
        
        while attempt < max_attempts:
            attempt += 1
            self.log_info(f"Executing script {script_id} (attempt {attempt}/{max_attempts})")
            
            # Update execution record if available
            if execution_obj:
                execution_obj.attempt_number = attempt
                execution_obj.save()
            
            try:
                # Find scene class in script
                scene_class = self._extract_scene_class(current_script)
                if not scene_class:
                    raise ValueError("Could not find a Scene class in the script")
                
                # Execute the script
                result = self._execute_script(current_script, scene_class, script_id)
                
                # If successful, update records and return
                if result["success"]:
                    self._update_success_records(execution_obj, result, start_time)
                    return {
                        "success": True,
                        "output_path": result["output_path"],
                        "execution": execution_obj,
                        "script": script_obj,
                        "scene_class": scene_class,
                        "attempt": attempt
                    }
                
                # Execution failed, try to handle the error
                last_error = result.get("error", "Unknown error")
                self.log_error(f"Execution failed: {last_error}")
                
                # Check for missing dependencies and install if needed
                if self._try_dependency_fix(last_error) and attempt < max_attempts:
                    self.log_info(f"Installed missing dependencies, retrying execution")
                    continue
                
                # Always try debugging the script with AI when there's an error
                if attempt < max_attempts:
                    self.log_info(f"Sending script to AI debugger (attempt {attempt})")
                    debug_result = self.debug_agent.debug(current_script, last_error, execution=execution_obj)
                    
                    # Always use the returned script, even if it's unchanged
                    current_script = debug_result["fixed_script"]
                    
                    if debug_result["changed"]:
                        self.log_info(f"AI provided a fixed script, retrying execution")
                    else:
                        self.log_warning(f"AI debugging did not change the script but will retry anyway")
                    
                    # Continue to retry with the current script (fixed or unchanged)
                    continue
                
            except Exception as e:
                error_msg = str(e)
                stack_trace = traceback.format_exc()
                self.log_error(f"Error in execution process: {error_msg}\n{stack_trace}")
                last_error = error_msg
                
                # Try debugging with AI if this is not the last attempt
                if attempt < max_attempts:
                    self.log_info(f"Sending script to AI debugger after exception (attempt {attempt})")
                    debug_result = self.debug_agent.debug(current_script, error_msg, execution=execution_obj)
                    current_script = debug_result["fixed_script"]
                    continue
        
        # All attempts failed, update records
        self._update_failure_records(execution_obj, last_error, start_time)
        
        return {
            "success": False,
            "error": last_error,
            "execution": execution_obj,
            "script": script_obj,
            "attempts": attempt
        }
    
    def _execute_script(self, script_content, scene_class, script_id):
        """
        Execute a Manim script in Docker
        
        Args:
            script_content (str): The script content to execute
            scene_class (str): The scene class to render
            script_id (str): Unique identifier for the script execution
            
        Returns:
            dict: Result with execution status, output path, and details
        """
        # Create a unique identifier for this execution
        execution_id = str(uuid.uuid4())
        temp_files = []
        
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w+", encoding="utf-8") as script_file:
                script_file.write(script_content)
                script_path = script_file.name
                temp_files.append(script_path)
                self.log_info(f"Created temporary script file at {script_path}")
            
            # Create temp file for output capture
            with tempfile.NamedTemporaryFile(prefix="manim_output_", suffix=".txt", delete=False, mode="w+", encoding="utf-8") as output_file:
                output_file_path = output_file.name
                temp_files.append(output_file_path)
            
            # Clean script if needed
            self._clean_script_file(script_path)
            
            # Prepare variables
            script_basename = os.path.basename(script_path).replace('.py', '')
            container_script_path = f"{self.working_dir}/{os.path.basename(script_path)}"
            
            # Copy script to container
            self.docker_agent.copy_to_container(
                self.container_name, 
                script_path, 
                container_script_path
            )
            
            # Execute manim in container
            cmd = f"python -m manim {os.path.basename(script_path)} {scene_class} -qm"
            result = self.docker_agent.execute_command(
                self.container_name,
                cmd,
                working_dir=self.working_dir
            )
            
            # Process output
            with open(output_file_path, "w", encoding="utf-8", errors="replace") as f:
                f.write(result["stdout"] + "\n" + result["stderr"])
            
            # Determine output path - Manim creates outputs in videos/script_basename/quality/scene.mp4
            output_dir = f"videos/{script_basename}/720p30"
            expected_output = f"{output_dir}/{scene_class}.mp4"
            full_output_path = os.path.join(self.media_root, expected_output)
            
            # Copy output from container if successful
            container_output_path = f"{self.working_dir}/{expected_output}"
            target_output_dir = os.path.join(self.media_root, output_dir)
            
            # Ensure target directory exists
            os.makedirs(target_output_dir, exist_ok=True)
            
            # Try to copy the output file from container
            if result["success"]:
                # Copy output file from container
                copy_result = self.docker_agent.copy_from_container(
                    self.container_name,
                    container_output_path,
                    full_output_path
                )
                
                if copy_result:
                    self.log_info(f"Copied output file to {full_output_path}")
                else:
                    self.log_error(f"Failed to copy output file from container")
                    result["success"] = False
            
            # Final check if output file exists
            if os.path.exists(full_output_path):
                self.log_info(f"Output file created: {full_output_path}")
                return {
                    "success": True,
                    "output": result["stdout"] + "\n" + result["stderr"],
                    "output_path": expected_output
                }
            else:
                # Extract error information
                error_info = result["stderr"] or "No output file generated"
                self.log_error(f"Output file not found: {error_info}")
                
                return {
                    "success": False,
                    "error": error_info,
                    "output": result["stdout"] + "\n" + result["stderr"]
                }
                
        except Exception as e:
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            self.log_error(f"Error in script execution: {error_msg}\n{stack_trace}")
            
            return {
                "success": False,
                "error": error_msg,
                "traceback": stack_trace
            }
            
        finally:
            # Clean up temporary files
            self._cleanup_temporary_files(temp_files, script_id)
    
    def _prepare_script(self, script):
        """
        Extract script content and ID from different input types
        
        Args:
            script (Script/str/dict): The script to execute
            
        Returns:
            tuple: (script_id, script_content, script_object)
        """
        script_id = str(uuid.uuid4())
        script_content = None
        script_obj = None
        
        # Check input type and extract content
        if isinstance(script, str):
            # Input is script content
            script_content = script
            
        elif hasattr(script, 'id') and hasattr(script, 'content'):
            # Input is a Script model object
            script_id = str(script.id)
            script_content = script.content
            script_obj = script
            
            # Update script status
            if hasattr(script, 'status'):
                script.status = 'executing'
                script.save()
                
        elif isinstance(script, dict) and 'content' in script:
            # Input is a dict with script content
            script_content = script['content']
            if 'id' in script:
                script_id = str(script['id'])
                
        else:
            raise ValueError("Invalid script input. Expected string, Script object, or dict with 'content' key.")
        
        return script_id, script_content, script_obj
    
    def _extract_scene_class(self, script_content):
        """
        Extract the scene class name from script content
        
        Args:
            script_content (str): Manim script content
            
        Returns:
            str: Scene class name or None if not found
        """
        # Look for class definition with Scene inheritance
        for line in script_content.split('\n'):
            if line.strip().startswith('class ') and '(Scene)' in line:
                return line.strip().split('class ')[1].split('(')[0].strip()
        
        return None
    
    def _clean_script_file(self, script_path):
        """
        Clean up script file content if needed
        
        Args:
            script_path (str): Path to the script file
            
        Returns:
            bool: True if cleaning was performed
        """
        try:
            with open(script_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                
            if "```python" in content or "```" in content:
                self.log_info(f"Cleaning script file: {script_path}")
                cleaned_content = content.replace("```python", "").replace("```", "").strip()
                
                with open(script_path, "w", encoding="utf-8", errors="replace") as f:
                    f.write(cleaned_content)
                self.log_info("Script cleaned")
                
                return True
                
        except Exception as e:
            self.log_error(f"Error cleaning script: {e}")
            
        return False
    
    def _cleanup_temporary_files(self, temp_files, script_id):
        """
        Clean up temporary files and directories
        
        Args:
            temp_files (list): List of temporary file paths to clean up
            script_id (str): Script ID for identifying related files
            
        Returns:
            bool: True if cleanup was successful
        """
        try:
            # Delete specific temp files
            for file_path in temp_files:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    self.log_debug(f"Deleted temp file: {file_path}")
            
            # Clean up Docker container temp files
            self.docker_agent.execute_command(
                self.container_name,
                f"rm -f {self.working_dir}/tmp*.py",
                working_dir=self.working_dir
            )
            
            # Comprehensive cleanup of other related temp files
            patterns = [
                os.path.join(tempfile.gettempdir(), "tmp*manim*"),
                os.path.join(tempfile.gettempdir(), f"*{script_id}*"),
                os.path.join(os.path.dirname(self.media_root), "tmp*.py")
            ]
            
            # Find and clean up matching files
            for pattern in patterns:
                for path in glob.glob(pattern):
                    try:
                        if os.path.isdir(path):
                            shutil.rmtree(path, ignore_errors=True)
                        else:
                            os.unlink(path)
                        self.log_debug(f"Cleaned up temp file: {path}")
                    except Exception as e:
                        self.log_debug(f"Failed to remove {path}: {str(e)}")
            
            return True
            
        except Exception as e:
            self.log_error(f"Error cleaning up temporary files: {str(e)}")
            return False
    
    def _try_dependency_fix(self, error_message):
        """
        Try to fix missing dependencies
        
        Args:
            error_message (str): Error message from execution
            
        Returns:
            bool: True if dependencies were installed
        """
        # Use dependency agent to detect and install missing deps
        result = self.dependency_agent.detect_and_install_missing_dependencies(
            error_message, 
            self.container_name
        )
        
        return result["success"]
    
    def _create_execution_record(self, script_obj, execution_id):
        """
        Create an execution record in the database
        
        Args:
            script_obj (Script): The script being executed
            execution_id (str): Unique ID for this execution
            
        Returns:
            Execution: The created execution record or None
        """
        if not script_obj:
            return None
            
        try:
            # Try to import Execution model - handle circular imports
            from ..models import Execution, Container
            
            # Get container record
            container = Container.objects.filter(name=self.container_name).first()
            
            # Create execution record
            execution = Execution.objects.create(
                id=execution_id,
                script=script_obj,
                attempt_number=1,
                container=container,
                is_successful=False
            )
            
            return execution
            
        except Exception as e:
            self.log_debug(f"Could not create execution record: {str(e)}")
            return None
    
    def _update_success_records(self, execution_obj, result, start_time):
        """
        Update records after successful execution
        
        Args:
            execution_obj (Execution): The execution record
            result (dict): Execution result
            start_time (datetime): When execution started
            
        Returns:
            Execution: Updated execution record
        """
        if not execution_obj:
            return None
            
        try:
            # Update execution record
            execution_obj.is_successful = True
            execution_obj.output = result.get("output", "")
            execution_obj.output_path = result.get("output_path", "")
            execution_obj.completed_at = timezone.now()
            execution_obj.save()
            
            # Update script status
            if hasattr(execution_obj, 'script') and execution_obj.script:
                execution_obj.script.status = 'successful'
                execution_obj.script.save()
                
            return execution_obj
            
        except Exception as e:
            self.log_error(f"Error updating success records: {str(e)}")
            return execution_obj
    
    def _update_failure_records(self, execution_obj, error, start_time):
        """
        Update records after failed execution
        
        Args:
            execution_obj (Execution): The execution record
            error (str): Error message
            start_time (datetime): When execution started
            
        Returns:
            Execution: Updated execution record
        """
        if not execution_obj:
            return None
            
        try:
            # Update execution record
            execution_obj.is_successful = False
            execution_obj.error = error
            execution_obj.completed_at = timezone.now()
            execution_obj.save()
            
            # Update script status
            if hasattr(execution_obj, 'script') and execution_obj.script:
                execution_obj.script.status = 'failed'
                execution_obj.script.save()
                
            return execution_obj
            
        except Exception as e:
            self.log_error(f"Error updating failure records: {str(e)}")
            return execution_obj 