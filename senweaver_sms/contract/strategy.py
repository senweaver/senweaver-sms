from abc import ABC, abstractmethod
from typing import Dict, List, Any
from .message import BaseMessage

class BaseStrategy(ABC):
    """
    Interface for SMS strategy implementations.
    """

    @abstractmethod
    def apply(self, gateways: Dict[str, Any], message: BaseMessage) -> List[str]:
        """
        Apply the strategy and return the ordered list of gateways to try.

        Args:
            gateways (Dict[str, Any]): Available gateways with their configs
            message (BaseMessage): The message to be sent

        Returns:
            List[str]: Ordered list of gateway names
        """
        pass