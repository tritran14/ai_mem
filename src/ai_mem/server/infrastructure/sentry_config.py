#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 22, 2025$"

import os
import logging
from typing import Optional

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

logger = logging.getLogger(__name__)


def _test_sentry_connection(dsn: str, timeout: int = 3) -> bool:
    """
    Test if Sentry server is reachable.
    
    Args:
        dsn: Sentry DSN to test
        timeout: Connection timeout in seconds
    
    Returns:
        True if server is reachable, False otherwise
    """
    try:
        from urllib.parse import urlparse
        import socket
        
        # Parse DSN to get host and port
        parsed = urlparse(dsn)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        
        # Try to connect to the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        
        return result == 0
    except Exception as e:
        logger.debug(f"Sentry connection test failed: {e}")
        return False


def init_sentry() -> None:
    """
    Initialize Sentry SDK for error tracking and performance monitoring.
    
    Configuration is loaded from environment variables:
    - SENTRY_DSN: Your Sentry DSN (required)
    - SENTRY_ENVIRONMENT: Environment name (default: development)
    - SENTRY_TRACES_SAMPLE_RATE: Percentage of transactions to track (0.0 to 1.0)
    - SENTRY_PROFILES_SAMPLE_RATE: Percentage of transactions to profile (0.0 to 1.0)
    
    The function will:
    1. Check if SENTRY_DSN is configured
    2. Test connection to Sentry server
    3. Initialize Sentry only if server is reachable
    
    If Sentry server is not reachable, the app will continue to run normally
    without error tracking.
    """
    sentry_dsn: Optional[str] = os.getenv("SENTRY_DSN")
    
    # Skip initialization if DSN is not configured
    if not sentry_dsn or sentry_dsn.startswith("http://YOUR_PUBLIC_KEY"):
        logger.debug("Sentry DSN not configured, running without error tracking")
        return
    
    # Test connection to Sentry server
    logger.debug("Testing connection to Sentry server...")
    if not _test_sentry_connection(sentry_dsn):
        logger.info("Sentry server is not available, running without error tracking")
        return
    
    environment: str = os.getenv("SENTRY_ENVIRONMENT", "development")
    traces_sample_rate: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))
    profiles_sample_rate: float = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "1.0"))
    
    # Configure logging integration
    # This will capture logs at ERROR level and above
    logging_integration = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors and above as events
    )
    
    try:
        # Suppress Sentry SDK's own logging to avoid warnings
        sentry_logger = logging.getLogger("sentry_sdk")
        sentry_logger.setLevel(logging.ERROR)  # Only show critical errors from SDK
        
        # Initialize Sentry
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                logging_integration,
            ],
            # Send default PII (Personally Identifiable Information)
            send_default_pii=False,
            # Attach stack traces to messages
            attach_stacktrace=True,
            # Enable performance monitoring
            enable_tracing=True,
            # Transport options to handle connection failures gracefully
            shutdown_timeout=2,  # Quick shutdown if server unavailable
        )
        
        logger.info(
            f"Sentry initialized successfully - Environment: {environment}, "
            f"Traces: {traces_sample_rate * 100}%, Profiles: {profiles_sample_rate * 100}%"
        )
    except Exception as e:
        # If Sentry initialization fails, log it but don't crash the app
        logger.warning(f"Failed to initialize Sentry: {e}. Continuing without error tracking.")
        return


def capture_exception(error: Exception, **extra_context) -> None:
    """
    Manually capture an exception and send it to Sentry.
    
    Args:
        error: The exception to capture
        **extra_context: Additional context to attach to the error
    
    Note:
        If Sentry is not initialized, this function does nothing.
    """
    if not sentry_sdk.Hub.current.client:
        return
    
    with sentry_sdk.push_scope() as scope:
        for key, value in extra_context.items():
            scope.set_extra(key, value)
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", **extra_context) -> None:
    """
    Manually capture a message and send it to Sentry.
    
    Args:
        message: The message to capture
        level: Severity level (debug, info, warning, error, fatal)
        **extra_context: Additional context to attach to the message
    
    Note:
        If Sentry is not initialized, this function does nothing.
    """
    if not sentry_sdk.Hub.current.client:
        return
    
    with sentry_sdk.push_scope() as scope:
        for key, value in extra_context.items():
            scope.set_extra(key, value)
        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: str, email: Optional[str] = None, **extra_data) -> None:
    """
    Set user context for Sentry events.
    
    Args:
        user_id: Unique user identifier
        email: User email (optional)
        **extra_data: Additional user data
    
    Note:
        If Sentry is not initialized, this function does nothing.
    """
    if not sentry_sdk.Hub.current.client:
        return
    
    user_data = {"id": user_id}
    if email:
        user_data["email"] = email
    user_data.update(extra_data)
    
    sentry_sdk.set_user(user_data)


def set_context(context_name: str, context_data: dict) -> None:
    """
    Set custom context for Sentry events.
    
    Args:
        context_name: Name of the context (e.g., "database", "api_call")
        context_data: Dictionary of context data
    
    Note:
        If Sentry is not initialized, this function does nothing.
    """
    if not sentry_sdk.Hub.current.client:
        return
    
    sentry_sdk.set_context(context_name, context_data)
