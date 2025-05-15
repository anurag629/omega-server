import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base class for all agents in the system.
    Provides common functionality and logging.
    """
    
    def __init__(self, debug=False):
        """
        Initialize the agent with debugging flag.
        """
        self.debug = debug
        self.logger = logger
    
    def log_info(self, message):
        """Log an info message with agent class info"""
        self.logger.info(f"[{self.__class__.__name__}] {message}")
    
    def log_error(self, message, exc_info=None):
        """Log an error message with agent class info"""
        self.logger.error(f"[{self.__class__.__name__}] {message}", exc_info=exc_info)
    
    def log_warning(self, message):
        """Log a warning message with agent class info"""
        self.logger.warning(f"[{self.__class__.__name__}] {message}")
    
    def log_debug(self, message):
        """Log a debug message with agent class info"""
        if self.debug:
            self.logger.debug(f"[{self.__class__.__name__}] {message}")
    
    def set_debug(self, debug=True):
        """Set the debug flag for this agent"""
        self.debug = debug
        return self 