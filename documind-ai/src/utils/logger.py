"""
DocuMind AI - Professional Logging System
Handles all application logging with rotation, multiple levels, and file output.
"""

import logging
import logging.config
import yaml
import os
from pathlib import Path
from typing import Optional


class LoggerSetup:
    """Setup and manage application logging."""
    
    def __init__(self, config_path: str = "config/logging.yaml"):
        self.config_path = config_path
        self.logger_initialized = False
    
    def setup(self) -> None:
        """Load logging configuration from YAML file."""
        if not os.path.exists(self.config_path):
            # Fallback to basic configuration
            self._setup_basic_logging()
            return
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Ensure log directory exists
            log_dir = "./logs"
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
            # Update file paths to be absolute
            for handler_name, handler_config in config.get('handlers', {}).items():
                if 'filename' in handler_config:
                    filename = handler_config['filename']
                    if not filename.startswith('/'):
                        handler_config['filename'] = os.path.join(log_dir, os.path.basename(filename))
            
            logging.config.dictConfig(config)
            self.logger_initialized = True
            
        except Exception as e:
            print(f"Warning: Could not load logging config: {e}")
            self._setup_basic_logging()
    
    def _setup_basic_logging(self):
        """Setup basic logging configuration as fallback."""
        log_dir = "./logs"
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(os.path.join(log_dir, 'app.log')),
            ]
        )
        self.logger_initialized = True


# Singleton instance
_logger_setup: Optional[LoggerSetup] = None


def setup_logging(config_path: str = "config/logging.yaml") -> None:
    """Initialize the logging system."""
    global _logger_setup
    _logger_setup = LoggerSetup(config_path)
    _logger_setup.setup()


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    if _logger_setup is None or not _logger_setup.logger_initialized:
        setup_logging()
    
    return logging.getLogger(name)


# Convenience function for module-level loggers
def get_module_logger(module_name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    logger = get_logger(f"app.{module_name}")
    return logger
