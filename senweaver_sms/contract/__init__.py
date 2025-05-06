"""
Exceptions module for SenWeaver SMS.

This module contains all the exceptions that can be raised by the SenWeaver SMS package.
"""

from .strategy import BaseStrategy
from .message import BaseMessage

__all__ = [
    'BaseStrategy',
    'BaseMessage'
] 