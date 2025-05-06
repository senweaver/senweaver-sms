"""
顺序策略 - 按照配置的顺序尝试网关
"""
from typing import Dict, List

from ..message import Message
from ..config import GatewayConfig
from .base import BaseStrategy


class OrderStrategy(BaseStrategy):
    """
    顺序策略
    
    按照配置的顺序尝试网关
    """
    
    def apply(self, gateways: Dict[str, GatewayConfig], message: Message) -> List[str]:
        """
        应用策略，选择网关
        
        按照配置的顺序返回网关名称列表
        
        Args:
            gateways: 可用的网关配置字典
            message: 要发送的消息
            
        Returns:
            网关名称列表，按照配置顺序排序
        """
        # 保持原始顺序
        return list(gateways.keys()) 