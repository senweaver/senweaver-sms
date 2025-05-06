from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseMessage(ABC):
    """
    Interface for SMS message implementations.
    """

    @abstractmethod
    def get_content(self, gateway=None) -> str:
        """
        Get the message content.

        Args:
            gateway: The gateway instance.

        Returns:
            str: The message content
        """
        pass

    @abstractmethod
    def get_template(self, gateway=None) -> str:
        """
        Get the message template ID.

        Args:
            gateway: The gateway instance.

        Returns:
            str: The message template ID
        """
        pass

    @abstractmethod
    def get_data(self, gateway=None) -> Dict[str, Any]:
        """
        Get the message template data.

        Args:
            gateway: The gateway instance.

        Returns:
            Dict[str, Any]: The message template data
        """
        pass

    @abstractmethod
    def get_strategy(self) -> Optional[str]:
        """
        Get the sending strategy.

        Returns:
            Optional[str]: The strategy class name
        """
        pass

    @abstractmethod
    def get_gateways(self) -> Optional[List[str]]:
        """
        Get the available gateways.

        Returns:
            Optional[List[str]]: The list of gateway names
        """
        pass