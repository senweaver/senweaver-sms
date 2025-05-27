"""
短信请求类 - 统一的短信发送入口
"""
from typing import Dict, Any, List, Union, Optional

from .config import SMSConfig, GatewayConfig
from .message import Message
from .phone_number import PhoneNumber
from .gateway.base import BaseGateway
from .strategy.base import BaseStrategy
from .strategy.order import OrderStrategy
from .response import SMSResponse, SMSBatchResponse
from .exception.exception import NoGatewayAvailableException, NoGatewaySelectedException, InvalidArgumentException



class SMSRequest:
    """
    短信请求类
    作为短信服务的主要入口点
    """
    
    def __init__(self, config: SMSConfig):
        """
        初始化
        
        Args:
            config: 短信配置
        """
        self.config = config
        self._strategies = {}
        self._gateways = {}
    
    def send(self, 
             to: Union[str, PhoneNumber], 
             content: str = None, 
             template: str = None, 
             data: Dict[str, Any] = None,
             gateways: List[str] = None,
             strategy: str = None) -> SMSResponse:
        """
        发送短信
        
        Args:
            to: 接收人手机号
            content: 短信内容，与template二选一
            template: 模板ID，与content二选一
            data: 模板参数
            gateways: 使用的网关列表，不指定则使用配置中的默认网关
            strategy: 使用的策略，不指定则使用配置中的默认策略
            
        Returns:
            发送结果
        """
        # 转换手机号为PhoneNumber对象
        phone = to if isinstance(to, PhoneNumber) else PhoneNumber(to)
        
        # 创建消息对象
        message = Message(
            content=content,
            template=template,
            data=data or {}
        )
        
        # 确定使用的网关列表
        gateway_names = self._get_gateway_names(gateways)
        
        # 获取策略
        strategy_name = strategy or self.config.default_strategy
        strategy_instance = self._get_strategy(strategy_name)
        
        # 应用策略选择网关
        gateway_configs = self._get_gateway_configs(gateway_names)
        selected_gateways = strategy_instance.apply(gateway_configs, message)
        
        # 发送消息
        return self._send_message(phone, message, selected_gateways)
        
    def _get_gateway_names(self, gateways: Optional[List[str]] = None) -> List[str]:
        """
        获取要使用的网关名称列表
        
        Args:
            gateways: 指定的网关列表
            
        Returns:
            网关名称列表
            
        Raises:
            NoGatewaySelectedException: 没有可用的网关时抛出
        """
        # 如果指定了网关，直接使用
        if gateways:
            return gateways
            
        # 如果有默认网关，使用默认网关
        if self.config.default_gateway:
            return [self.config.default_gateway]
            
        # 否则使用所有配置的网关
        if self.config.gateways:
            return list(self.config.gateways.keys())
            
        # 没有可用的网关
        raise NoGatewaySelectedException("未指定任何网关，且没有配置默认网关")
        
    def _get_gateway(self, name: str) -> BaseGateway:
        """
        获取网关实例
        
        Args:
            name: 网关名称
            
        Returns:
            网关实例
        """
        if name not in self._gateways:
            self._gateways[name] = self._create_gateway(name)
            
        return self._gateways[name]
        
    def _get_strategy(self, name: str) -> BaseStrategy:
        """
        获取策略实例
        
        Args:
            name: 策略名称
            
        Returns:
            策略实例
        """
        if name not in self._strategies:
            self._strategies[name] = self._create_strategy(name)
            
        return self._strategies[name]
        
    def _get_gateway_configs(self, gateway_names: List[str]) -> Dict[str, GatewayConfig]:
        """
        获取指定网关的配置
        
        Args:
            gateway_names: 网关名称列表
            
        Returns:
            网关配置字典
        """
        configs = {}
        for name in gateway_names:
            config = self.config.get_gateway(name)
            if config:
                configs[name] = config
        return configs
        
    def _send_message(self, to: PhoneNumber, message: Message, gateway_names: List[str]) -> SMSResponse:
        """
        使用指定网关发送消息
        
        Args:
            to: 接收人手机号
            message: 消息对象
            gateway_names: 网关名称列表
            
        Returns:
            发送结果
            
        Raises:
            NoGatewayAvailableException: 所有网关都发送失败时抛出
        """
        responses = SMSBatchResponse()
        
        for name in gateway_names:
            try:
                # 获取网关和配置
                gateway = self._get_gateway(name)
                config = self.config.get_gateway(name)
                
                if not config:
                    continue
                    
                # 发送短信
                response = gateway.send(to, message, config)
                responses.add_response(response)
                
                # 如果发送成功，直接返回
                if response.is_success:
                    return response
            except Exception as e:
                # 记录错误但继续尝试下一个网关
                response = SMSResponse.failed(
                    gateway=name,
                    phone_number=to.get_number(),
                    error_code="UNKNOWN_ERROR",
                    error_message=str(e)
                )
                responses.add_response(response)
                continue
                
        # 所有网关都发送失败，抛出异常
        if responses.is_failed:
            raise NoGatewayAvailableException(
                "所有网关均发送失败",
                {"responses": responses.get_failed_responses()}
            )
            
        # 如果没有任何响应（不太可能发生）
        if not responses.responses:
            raise NoGatewayAvailableException("未找到任何有效的网关")
            
        # 返回最后一个响应（通常不会执行到这里）
        return responses.responses[-1]
        
    def _create_gateway(self, name: str) -> BaseGateway:
        """
        创建网关实例
        
        Args:
            name: 网关名称
            
        Returns:
            网关实例
            
        Raises:
            InvalidArgumentException: 无法创建网关时抛出
        """
        try:
            import importlib
            
            # 尝试导入网关模块
            module_name = f".gateway.{name}"
            module = importlib.import_module(module_name, package="senweaver_sms")
            
            # 查找网关类
            gateway_class_name = "".join(word.capitalize() for word in name.split("_")) + "Gateway"
            if hasattr(module, gateway_class_name):
                return getattr(module, gateway_class_name)()
        except ImportError:
            pass
            
        raise InvalidArgumentException(f"未找到网关: {name}")
        
    def _create_strategy(self, name: str) -> BaseStrategy:
        """
        创建策略实例
        
        Args:
            name: 策略名称
            
        Returns:
            策略实例
            
        Raises:
            InvalidArgumentException: 无法创建策略时抛出
        """
        if name == "order":
            return OrderStrategy()
            
        try:
            import importlib
            
            # 尝试导入策略模块
            module_name = f".strategy.{name}"
            module = importlib.import_module(module_name, package="senweaver_sms")
            
            # 查找策略类
            strategy_class_name = "".join(word.capitalize() for word in name.split("_")) + "Strategy"
            if hasattr(module, strategy_class_name):
                return getattr(module, strategy_class_name)()
        except ImportError:
            pass
            
        raise InvalidArgumentException(f"未找到策略: {name}")
        
    @classmethod
    def create(cls, config: SMSConfig) -> 'SMSRequest':
        """
        创建短信请求实例
        
        Args:
            config: 短信配置
            
        Returns:
            短信请求实例
        """
        return cls(config)

    def batch_send(self, 
                   to_list: List[Union[str, PhoneNumber]], 
                   content: str = None, 
                   template: str = None, 
                   data: Dict[str, Any] = None,
                   gateways: List[str] = None,
                   strategy: str = None) -> SMSBatchResponse:
        """
        批量发送短信
        
        Args:
            to_list: 接收人手机号列表
            content: 短信内容
            template: 模板ID
            data: 模板参数
            gateways: 使用的网关列表
            strategy: 使用的策略
            
        Returns:
            批量发送结果
        """
        # 创建批量响应对象
        batch_response = SMSBatchResponse()
        
        # 逐个发送
        for to in to_list:
            try:
                response = self.send(to, content, template, data, gateways, strategy)
                batch_response.add_response(response)
            except Exception as e:
                # 单个发送失败不影响其他发送
                phone = to if isinstance(to, PhoneNumber) else PhoneNumber(to)
                response = SMSResponse.failed(
                    gateway="unknown",
                    phone_number=phone.get_number(),
                    error_code="SEND_FAILED",
                    error_message=str(e)
                )
                batch_response.add_response(response)
                
        return batch_response 