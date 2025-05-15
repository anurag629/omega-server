import os
import subprocess
import traceback
from django.utils import timezone
from .base_agent import BaseAgent

class DockerAgent(BaseAgent):
    """
    Agent responsible for Docker container operations.
    Handles container status checking, starting, stopping, and command execution.
    """
    
    def __init__(self, debug=False):
        """Initialize the Docker agent"""
        super().__init__(debug)
        
    def check_container_status(self, container_name):
        """
        Check if a Docker container is running
        
        Args:
            container_name (str): Name of the container to check
            
        Returns:
            bool: True if container is running, False otherwise
        """
        try:
            # Check if container exists and is running
            check_cmd = ["docker", "container", "inspect", "-f", "{{.State.Running}}", container_name]
            result = subprocess.run(
                check_cmd, 
                capture_output=True, 
                text=True,
                encoding="utf-8", 
                errors="replace"
            )
            
            if result.returncode != 0:
                self.log_warning(f"Docker container {container_name} does not exist or is not accessible")
                return False
                
            # Update container status in database if available
            self._update_container_status(container_name, result.stdout.strip() == "true")
            
            return result.stdout.strip() == "true"
                
        except Exception as e:
            self.log_error(f"Error checking Docker container status: {str(e)}")
            return False
    
    def ensure_container_running(self, container_name):
        """
        Check if the Docker container is running and start it if needed
        
        Args:
            container_name (str): Name of the container to check/start
            
        Returns:
            bool: True if container is running (or started successfully), False otherwise
        """
        try:
            # First check if it's already running
            if self.check_container_status(container_name):
                self.log_info(f"Docker container {container_name} is already running")
                return True
                
            # Container exists but is not running, try to start it
            self.log_info(f"Starting Docker container {container_name}")
            start_cmd = ["docker", "start", container_name]
            start_result = subprocess.run(
                start_cmd, 
                capture_output=True, 
                text=True,
                encoding="utf-8", 
                errors="replace"
            )
            
            if start_result.returncode == 0:
                self.log_info(f"Successfully started Docker container {container_name}")
                # Update status in database
                self._update_container_status(container_name, True)
                return True
            else:
                self.log_error(f"Failed to start Docker container: {start_result.stderr}")
                return False
                
        except Exception as e:
            self.log_error(f"Error ensuring Docker container is running: {str(e)}")
            return False
    
    def execute_command(self, container_name, command, working_dir=None):
        """
        Execute a command in a Docker container
        
        Args:
            container_name (str): Name of the container to run command in
            command (str): Command to execute
            working_dir (str, optional): Working directory in container. Defaults to None.
            
        Returns:
            dict: Result with stdout, stderr, and success status
        """
        try:
            # Ensure container is running
            if not self.ensure_container_running(container_name):
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Container {container_name} is not running",
                    "error": f"Failed to start container {container_name}"
                }
            
            # Build the command - with working directory if specified
            if working_dir:
                cmd = f"cd {working_dir} && {command}"
            else:
                cmd = command
                
            # Execute command in container
            self.log_info(f"Executing command in container {container_name}: {cmd}")
            process = subprocess.run(
                ["docker", "exec", container_name, "bash", "-c", cmd],
                capture_output=True,
                text=True,
                encoding="utf-8", 
                errors="replace"
            )
            
            # Return results
            success = process.returncode == 0
            if success:
                self.log_info(f"Command executed successfully in container {container_name}")
            else:
                self.log_error(f"Command execution failed in container {container_name}: {process.stderr}")
                
            return {
                "success": success,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "returncode": process.returncode
            }
            
        except Exception as e:
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            self.log_error(f"Error executing command in Docker container: {error_msg}\n{stack_trace}")
            
            return {
                "success": False,
                "stdout": "",
                "stderr": error_msg,
                "error": stack_trace
            }
    
    def copy_to_container(self, container_name, source_path, dest_path):
        """
        Copy a file from host to container
        
        Args:
            container_name (str): Name of the target container
            source_path (str): Path to source file on host
            dest_path (str): Path to destination in container
            
        Returns:
            bool: True if copy successful, False otherwise
        """
        try:
            self.log_info(f"Copying {source_path} to container {container_name}:{dest_path}")
            copy_cmd = ["docker", "cp", source_path, f"{container_name}:{dest_path}"]
            result = subprocess.run(
                copy_cmd, 
                check=True, 
                capture_output=True, 
                encoding="utf-8", 
                errors="replace"
            )
            
            if result.returncode == 0:
                self.log_info(f"Successfully copied file to container")
                return True
            else:
                self.log_error(f"Failed to copy file to container: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_error(f"Error copying file to container: {str(e)}")
            return False
    
    def copy_from_container(self, container_name, source_path, dest_path):
        """
        Copy a file from container to host
        
        Args:
            container_name (str): Name of the source container
            source_path (str): Path to source file in container
            dest_path (str): Path to destination on host
            
        Returns:
            bool: True if copy successful, False otherwise
        """
        try:
            self.log_info(f"Copying from container {container_name}:{source_path} to {dest_path}")
            copy_cmd = ["docker", "cp", f"{container_name}:{source_path}", dest_path]
            result = subprocess.run(
                copy_cmd, 
                check=True, 
                capture_output=True, 
                encoding="utf-8", 
                errors="replace"
            )
            
            if result.returncode == 0:
                self.log_info(f"Successfully copied file from container")
                return True
            else:
                self.log_error(f"Failed to copy file from container: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_error(f"Error copying file from container: {str(e)}")
            return False
    
    def _update_container_status(self, container_name, is_running):
        """
        Update container status in database if container model exists
        
        Args:
            container_name (str): Name of the container
            is_running (bool): Current running status
            
        Returns:
            bool: True if status updated in database, False otherwise
        """
        try:
            # Try to import Container model - handle circular imports
            from ..models import Container
            
            # Find container in database and update status
            container = Container.objects.filter(name=container_name).first()
            if container:
                container.is_running = is_running
                container.last_checked = timezone.now()
                container.save()
                return True
            return False
        except Exception:
            # This is expected during early setup when database might not be ready
            # or when running outside of Django context
            return False 