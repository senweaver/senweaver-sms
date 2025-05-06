import importlib
import inspect
from typing import Dict, Any, List, Union, Callable, Type

from .phone_number import PhoneNumber
from .message import Message, BaseMessage
from .contract import BaseStrategy
from .gateway import BaseGateway
from .exception import NoGatewayAvailableException
from .exception import NoGatewaySelectedException
from .exception import InvalidArgumentException

class SenWeaverSMS:
    """
    The main class for SenWeaver SMS.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize a new instance.

        Args:
            config (Dict[str, Any]): The configuration
        """
        self.config = config
        self._strategies = {}
        self._gateways = {}
        self._gateway_factory = {}

    def send(self, to: Union[str, PhoneNumber], message: Union[BaseMessage, Dict[str, Any]], gateways: List[str] = None) -> Dict[str, Any]:
        """
        Send a message.

        Args:
            to (Union[str, PhoneNumber]): The recipient's phone number
            message (Union[BaseMessage, Dict[str, Any]]): The message to send or a dict to create a Message
            gateways (List[str], optional): The gateways to use. Defaults to None.

        Raises:
            NoGatewayAvailableException: When none of the gateways could send the message
            NoGatewaySelectedException: When no gateway is selected

        Returns:
            Dict[str, Any]: The responses from the gateways
        """
        # Convert raw array to message
        if isinstance(message, dict):
            message = Message(**message)

        # Get default gateways if not provided
        if gateways is None:
            gateways = message.get_gateways() or self.get_config().get('default', {}).get('gateways', [])

        if not gateways:
            raise NoGatewaySelectedException('No gateway selected.')

        # Get strategy from message or default
        strategy_name = message.get_strategy() or self.get_config().get('default', {}).get('strategy')
        strategy = self.get_strategy(strategy_name)

        # Apply strategy to get order of gateways
        selected_gateways = strategy.apply(
            self._get_gateway_configs(gateways),
            message
        )

        return self._send_message(to, message, selected_gateways)

    def extend(self, gateway_name: str, gateway_factory: Callable) -> None:
        """
        Extend the SMS class with a custom gateway.

        Args:
            gateway_name (str): The name of the gateway
            gateway_factory (Callable): The factory function to create the gateway
        """
        self._gateway_factory[gateway_name.lower()] = gateway_factory

    def get_gateway(self, name: str) -> BaseGateway:
        """
        Get a gateway instance by name.

        Args:
            name (str): The gateway name

        Returns:
            BaseGateway: The gateway instance
        """
        name = name.lower()
        
        if name not in self._gateways:
            self._gateways[name] = self._create_gateway(name)
        
        return self._gateways[name]

    def get_strategy(self, strategy: Union[str, Type[BaseStrategy]]) -> BaseStrategy:
        """
        Get a strategy instance.

        Args:
            strategy (Union[str, Type[BaseStrategy]]): The strategy name or class

        Returns:
            BaseStrategy: The strategy instance
        """
        if isinstance(strategy, str):
            if strategy not in self._strategies:
                self._strategies[strategy] = self._create_strategy(strategy)
            return self._strategies[strategy]
        
        return strategy()

    def get_config(self) -> Dict[str, Any]:
        """
        Get the configuration.

        Returns:
            Dict[str, Any]: The configuration
        """
        return self.config

    def _get_gateway_configs(self, gateways: List[str]) -> Dict[str, Any]:
        """
        Get the configurations for the specified gateways.

        Args:
            gateways (List[str]): The gateway names

        Returns:
            Dict[str, Any]: The gateway configurations
        """
        configs = {}
        for gateway in gateways:
            if gateway in self.config:
                configs[gateway] = self.config[gateway]
        return configs

    def _send_message(self, to: Union[str, PhoneNumber], message: BaseMessage, gateway_names: List[str]) -> Dict[str, Any]:
        """
        Send a message using the specified gateways.

        Args:
            to (Union[str, PhoneNumber]): The recipient's phone number
            message (BaseMessage): The message to send
            gateway_names (List[str]): The gateway names to try

        Raises:
            NoGatewayAvailableException: When none of the gateways could send the message

        Returns:
            Dict[str, Any]: The responses from the gateways
        """
        responses = {}
        last_exception = None

        for gateway_name in gateway_names:
            try:
                gateway = self.get_gateway(gateway_name)
                response = gateway.send(to, message, self.config.get(gateway_name))
                responses[gateway_name] = response
                return responses
            except Exception as e:
                last_exception = e
                continue

        if last_exception:
            raise NoGatewayAvailableException('No gateway could send the message.') from last_exception

        return responses

    def _create_gateway(self, name: str) -> BaseGateway:
        """
        Create a gateway instance.

        Args:
            name (str): The gateway name

        Returns:
            BaseGateway: The gateway instance

        Raises:
            InvalidArgumentException: When the gateway is not found
        """
        if name in self._gateway_factory:
            return self._gateway_factory[name]()

        try:
            module = importlib.import_module(f'.gateways.{name}', package='senweaver_sms')
            for item in dir(module):
                if item.endswith('Gateway') and item != 'Gateway':
                    return getattr(module, item)()
        except ImportError:
            pass

        raise InvalidArgumentException(f'Gateway "{name}" not found.')

    def _create_strategy(self, name: str) -> BaseStrategy:
        """
        Create a strategy instance.

        Args:
            name (str): The strategy name

        Returns:
            BaseStrategy: The strategy instance

        Raises:
            InvalidArgumentException: When the strategy is not found
        """
        try:
            module = importlib.import_module(f'.strategy.{name}', package='senweaver_sms')
            for item in dir(module):
                if item.endswith('Strategy') and item != 'Strategy':
                    return getattr(module, item)()
        except ImportError:
            pass

        raise InvalidArgumentException(f'Strategy "{name}" not found.') 