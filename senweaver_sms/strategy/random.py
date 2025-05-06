import random
from typing import Dict, List, Any
from ..contract import BaseStrategy
from ..message import Message

class RandomStrategy(BaseStrategy):
    """
    Random Strategy.
    
    This strategy sends messages through gateways in a random order.
    """

    def apply(self, gateways: Dict[str, Any], message: Message) -> List[str]:
        """
        Apply the strategy and return a randomized list of gateways.

        Args:
            gateways (Dict[str, Any]): Available gateways with their configs
            message (Message): The message to be sent

        Returns:
            List[str]: Randomized list of gateway names
        """
        gateway_names = list(gateways.keys())
        random.shuffle(gateway_names)
        return gateway_names 