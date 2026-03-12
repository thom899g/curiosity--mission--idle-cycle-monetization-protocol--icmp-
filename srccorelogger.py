"""
Unified logging system for CURIOSITY ICMP with structured logging and error tracking.
"""
import structlog
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import json

def setup_logger(level: str = "INFO", component: str = "system") -> structlog.BoundLogger:
    """
    Configure structured logging with proper formatting and error handling.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        component: Component name for log identification
    
    Returns:
        Configured logger instance
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper())
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    logger = structlog.get_logger(component)
    logger.info("logger_initialized", component=component, level=level)
    return logger

class LoggingMiddleware:
    """Middleware for capturing and logging system events with context."""
    
    def __init__(self, logger: structlog.BoundLogger):
        self.logger = logger
        self.metrics: Dict[str, Any] = {
            "start_time": datetime.utcnow().isoformat(),
            "errors": 0,
            "warnings": 0,
            "transactions": 0
        }
    
    def log_event(self, 
                  event: str, 
                  level: str = "info", 
                  **kwargs) -> None:
        """Log structured event with context."""
        log_method = getattr(self.logger, level)
        
        # Add system context
        context = {
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "system_uptime": self._calculate_uptime(),
            **kwargs
        }
        
        # Update metrics
        if level == "error":
            self.metrics["errors"] += 1
        elif level == "warning":
            self.metrics["warnings"] += 1
        
        log_method(event, **context)
    
    def _calculate_uptime(self) -> str:
        """Calculate system uptime in human-readable format."""
        start = datetime.fromisoformat(self.metrics["start_time"])
        delta = datetime.utcnow() - start
        return str(delta)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current logging metrics."""
        return self.metrics.copy()