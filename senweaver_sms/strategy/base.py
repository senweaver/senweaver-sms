"""
策略基类 - 定义所有策略的基本接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List

from ..message import Message
from ..config import GatewayConfig


class BaseStrategy(ABC):
    """
    策略基类
    定义所有策略必须实现的接口
    """
    
    @abstractmethod
    def apply(self, gateways: Dict[str, GatewayConfig], message: Message) -> List[str]:
        """
        应用策略，选择网关
        
        Args:
            gateways: 可用的网关配置字典
            message: 要发送的消息
            
        Returns:
            选择的网关名称列表，按照尝试顺序排序
        """
        pass 