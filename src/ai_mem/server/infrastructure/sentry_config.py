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


def init_sentry() -> None:
    """
    Initialize Sentry SDK for error tracking and performance monitoring.
    
    Configuration is loaded from environment variables:
    - SENTRY_DSN: Your Sentry DSN (required)
    - SENTRY_ENVIRONMENT: Environment name (default: development)
    - SENTRY_TRACES_SAMPLE_RATE: Percentage of transactions to track (0.0 to 1.0)
    - SENTRY_PROFILES_SAMPLE_RATE: Percentage of transactions to profile (0.0 to 1.0)
    """
    sentry_dsn: Optional[str] = os.getenv("SENTRY_DSN")
    
    # Skip initialization if DSN is not configured
    if not sentry_dsn or sentry_dsn.startswith("http://YOUR_PUBLIC_KEY"):
        logger.info("Sentry DSN not configured, skipping Sentry initialization")
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
    )
    
    logger.info(
        f"Sentry initialized successfully - Environment: {environment}, "
        f"Traces: {traces_sample_rate * 100}%, Profiles: {profiles_sample_rate * 100}%"
    )


def capture_exception(error: Exception, **extra_context) -> None:
    """
    Manually capture an exception and send it to Sentry.
    
    Args:
        error: The exception to capture
        **extra_context: Additional context to attach to the error
    """
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
    """
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
    """
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
    """
    sentry_sdk.set_context(context_name, context_data)
