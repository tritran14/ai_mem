#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 22, 2025 12:09:13$"

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


class EmptyFactsLogger:
    """
    Dedicated logger for empty facts cases.
    
    Logs only the raw LLM response when facts extraction returns empty,
    making it easy to analyze why the LLM couldn't extract facts.
    """
    
    def __init__(
        self,
        log_file: str = None,
        log_dir: str = None,
    ):
        """
        Initialize empty facts logger.
        
        Args:
            log_file: Log file name (default: empty_facts.log)
            log_dir: Directory for log files (default: logs/)
        """
        log_file = log_file or os.getenv("EMPTY_FACTS_LOG_FILE", "empty_facts.log")
        log_dir = log_dir or os.getenv("LOG_DIR", "logs")
        
        # Create logs directory
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Full path to log file
        self.log_file_path = log_path / log_file
        
        # Create dedicated logger
        self.logger = logging.getLogger("empty_facts")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # Don't propagate to root logger
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # File handler with rotation (max 5MB, keep 3 backups)
        file_handler = RotatingFileHandler(
            self.log_file_path,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        
        # Simple format - just timestamp and message
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def log_empty_facts(self, original_message: str, llm_response: str):
        """
        Log an empty facts case.
        
        Args:
            original_message: The original user message
            llm_response: The raw LLM response
        """
        separator = "=" * 80
        
        self.logger.info(separator)
        self.logger.info(f"Original Message: {original_message}")
        self.logger.info(f"LLM Response:\n{llm_response}")
        self.logger.info(separator)
        self.logger.info("")  # Empty line for readability


# Global instance
_empty_facts_logger = None


def get_empty_facts_logger() -> EmptyFactsLogger:
    """
    Get the global empty facts logger instance.
    
    Returns:
        EmptyFactsLogger instance
    """
    global _empty_facts_logger
    if _empty_facts_logger is None:
        _empty_facts_logger = EmptyFactsLogger()
    return _empty_facts_logger
