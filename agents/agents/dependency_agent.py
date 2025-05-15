import re
import traceback
from .base_agent import BaseAgent
from .docker_agent import DockerAgent

class DependencyAgent(BaseAgent):
    """
    Agent responsible for managing dependencies required by Manim scripts.
    Detects missing dependencies and installs them in the Docker container.
    """
    
    def __init__(self, debug=False):
        """Initialize the Dependency Agent"""
        super().__init__(debug)
        self.docker_agent = DockerAgent(debug)
    
    def detect_and_install_missing_dependencies(self, error_message, container_name="omega-manim"):
        """
        Detect missing dependencies from error message and install them
        
        Args:
            error_message (str): Error message from script execution
            container_name (str, optional): Docker container name. Defaults to "omega-manim".
            
        Returns:
            dict: Result with installed packages and success flag
        """
        missing_modules = self._extract_missing_modules(error_message)
        
        if not missing_modules:
            self.log_info("No missing dependencies detected in error message")
            return {
                "success": False,
                "message": "No missing dependencies detected",
                "installed": []
            }
        
        # Try to install each missing dependency
        installed_modules = []
        failed_modules = []
        
        for module_name in missing_modules:
            result = self.install_dependency(module_name, container_name)
            if result["success"]:
                installed_modules.append(module_name)
            else:
                failed_modules.append({
                    "module": module_name,
                    "error": result.get("error", "Unknown error")
                })
        
        return {
            "success": len(installed_modules) > 0,
            "message": f"Installed {len(installed_modules)} dependencies",
            "installed": installed_modules,
            "failed": failed_modules
        }
    
    def install_dependency(self, module_name, container_name="omega-manim"):
        """
        Install a dependency in the Docker container
        
        Args:
            module_name (str): Name of the Python module to install
            container_name (str, optional): Docker container name. Defaults to "omega-manim".
            
        Returns:
            dict: Result with success flag and error message if any
        """
        try:
            # Sanitize module name for security
            if not self._is_valid_module_name(module_name):
                return {
                    "success": False,
                    "error": f"Invalid module name: {module_name}"
                }
            
            # Install module in container
            self.log_info(f"Installing module {module_name} in container {container_name}")
            install_command = f"pip install {module_name}"
            
            # Execute installation
            result = self.docker_agent.execute_command(container_name, install_command)
            
            if result["success"]:
                self.log_info(f"Successfully installed {module_name} in container")
                return {
                    "success": True,
                    "module": module_name,
                    "output": result["stdout"]
                }
            else:
                self.log_error(f"Failed to install {module_name}: {result['stderr']}")
                return {
                    "success": False,
                    "module": module_name,
                    "error": result["stderr"]
                }
                
        except Exception as e:
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            self.log_error(f"Error installing dependency: {error_msg}\n{stack_trace}")
            
            return {
                "success": False,
                "module": module_name,
                "error": error_msg
            }
    
    def _extract_missing_modules(self, error_message):
        """
        Extract names of missing modules from error message
        
        Args:
            error_message (str): Error message from script execution
            
        Returns:
            list: List of missing module names
        """
        # Initialize list for missing modules
        missing_modules = []
        
        if not error_message:
            return missing_modules
            
        # Check for common import error patterns
        if "No module named" in error_message:
            # Extract module names from error message
            no_module_matches = re.findall(r"No module named ['\"]([^'\"]+)['\"]", error_message)
            missing_modules.extend(no_module_matches)
            
        # Check for ImportError patterns
        if "ImportError:" in error_message:
            # Try to extract module names from ImportError lines
            import_error_lines = [line for line in error_message.split('\n') if "ImportError:" in line]
            for line in import_error_lines:
                # Look for patterns like "ImportError: cannot import name X from Y"
                if "from" in line:
                    module_match = re.search(r"from ['\"]?([^'\"]+)['\"]?", line)
                    if module_match:
                        missing_modules.append(module_match.group(1))
                # Look for direct module imports
                else:
                    module_match = re.search(r"ImportError: ([^:]+)", line)
                    if module_match:
                        module_name = module_match.group(1).strip()
                        # Clean up the module name
                        module_name = re.sub(r"^cannot import |^No module named ", "", module_name)
                        module_name = module_name.strip("'\"")
                        if module_name and self._is_valid_module_name(module_name):
                            missing_modules.append(module_name)
        
        # Deduplicate and sanitize
        sanitized_modules = []
        for module in missing_modules:
            # Extract base module name (before the first dot)
            base_module = module.split('.')[0].strip()
            if base_module and base_module not in sanitized_modules and self._is_valid_module_name(base_module):
                sanitized_modules.append(base_module)
        
        self.log_info(f"Detected missing modules: {sanitized_modules}")
        return sanitized_modules
    
    def _is_valid_module_name(self, module_name):
        """
        Check if a module name is valid and safe to install
        
        Args:
            module_name (str): Name of the module to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Basic validation for security
        if not module_name or not isinstance(module_name, str):
            return False
            
        # Check for valid Python package name (alphanumeric, underscores, dots)
        if not re.match(r'^[a-zA-Z0-9_.-]+$', module_name):
            return False
            
        # Check for potential security issues
        if any(char in module_name for char in ';&|$()`\\/'):
            return False
            
        # Blacklist of dangerous packages
        blacklist = ['os', 'sys', 'subprocess', 'shutil', 'pathlib', 'logging']
        if module_name.lower() in blacklist:
            return False
            
        return True 