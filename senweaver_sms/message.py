from typing import Dict, Any, Optional, List
from .contract.message import BaseMessage

class Message(BaseMessage):
    """
    Class representing an SMS message.
    """

    # Default strategy and gateways, to be overridden by subclasses if needed
    strategy = None
    gateways = None

    def __init__(self, **kwargs):
        """
        Initialize a new message.

        Args:
            **kwargs: Additional attributes for the message
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_content(self, gateway=None) -> str:
        """
        Get the message content.

        Args:
            gateway: The gateway instance. Defaults to None.

        Returns:
            str: The message content
        """
        if hasattr(self, 'content'):
            if callable(self.content):
                return self.content(gateway)
            return self.content
        
        return ''

    def get_template(self, gateway=None) -> str:
        """
        Get the message template ID.

        Args:
            gateway: The gateway instance. Defaults to None.

        Returns:
            str: The message template ID
        """
        if hasattr(self, 'template'):
            if callable(self.template):
                return self.template(gateway)
            return self.template
        
        return ''

    def get_data(self, gateway=None) -> Dict[str, Any]:
        """
        Get the message template data.

        Args:
            gateway: The gateway instance. Defaults to None.

        Returns:
            Dict[str, Any]: The message template data
        """
        if hasattr(self, 'data'):
            if callable(self.data):
                return self.data(gateway)
            return self.data
        
        return {}

    def get_strategy(self) -> Optional[str]:
        """
        Get the sending strategy.

        Returns:
            Optional[str]: The strategy class name
        """
        return self.strategy

    def get_gateways(self) -> Optional[List[str]]:
        """
        Get the available gateways.

        Returns:
            Optional[List[str]]: The list of gateway names
        """
        return self.gateways 