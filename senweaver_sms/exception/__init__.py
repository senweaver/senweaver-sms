"""
Exceptions module for SenWeaver SMS.

This module contains all the exceptions that can be raised by the SenWeaver SMS package.
"""

from .exception import Exception, GatewayErrorException, InvalidArgumentException, NoGatewayAvailableException, NoGatewaySelectedException

__all__ = [
    'Exception',
    'GatewayErrorException',
    'InvalidArgumentException',
    'NoGatewayAvailableException',
    'NoGatewaySelectedException',
] 