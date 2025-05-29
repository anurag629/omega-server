from django.conf import settings

class BaseAgent:
    """
    Base class for all agents in the system.
    Provides common functionality.
    """
    
    def __init__(self, debug=False):
        """
        Initialize the agent with debugging flag.
        """
        self.debug = debug
    
    def log_info(self, message):
        """Log an info message with agent class info"""
        pass
    
    def log_error(self, message, exc_info=None):
        """Log an error message with agent class info"""
        pass
    
    def log_warning(self, message):
        """Log a warning message with agent class info"""
        pass
    
    def log_debug(self, message):
        """Log a debug message with agent class info"""
        pass
    
    def set_debug(self, debug=True):
        """Set the debug flag for this agent"""
        self.debug = debug
        return self 