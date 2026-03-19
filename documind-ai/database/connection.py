"""Database connection manager"""

import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.db_url = os.environ.get('DATABASE_URL', 'sqlite:///data/documind.db')
        self.connection = None
        self._initialized = True
        logger.info("Database connection initialized")
    
    def connect(self):
        """Establish database connection"""
        logger.info(f"Connecting to database: {self.db_url}")
        # Implementation depends on chosen DB
        return self
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

db = DatabaseConnection()
