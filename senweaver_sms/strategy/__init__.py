"""
Strategy module for SenWeaver SMS.

This module contains various strategy for sending SMS messages through multiple gateways.
"""

from .order import OrderStrategy
from .random import RandomStrategy

__all__ = ['OrderStrategy', 'RandomStrategy'] 