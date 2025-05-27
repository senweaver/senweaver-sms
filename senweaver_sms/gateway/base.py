"""
网关基类 - 定义所有短信网关的基本接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from ..phone_number import PhoneNumber
from ..message import Message
from ..response import SMSResponse
from ..exception.exception import GatewayErrorException
from ..config import GatewayConfig


class BaseGateway(ABC):
    """
    网关基类
    定义所有短信网关必须实现的接口
    """
    
    @abstractmethod
    def _send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """
        发送短信的具体实现
        所有子类必须实现此方法
        
        Args:
            to: 接收人手机号
            message: 短信消息
            config: 网关配置
            
        Returns:
            网关的原始响应
        """
        pass
    
    def send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> SMSResponse:
        """
        发送短信
        处理请求和响应，捕获异常
        
        Args:
            to: 接收人手机号
            message: 短信消息
            config: 网关配置
            
        Returns:
            统一的SMS响应对象
        """
        # 获取网关名称
        gateway_name = self._get_gateway_name()
        
        try:
            # 验证必要的配置
            self._validate_config(config)
            
            # 调用具体的发送实现
            response = self._send(to, message, config)
            
            # 提取消息ID
            message_id = self._extract_message_id(response)
            
            # 计算计费条数
            fee = self._calculate_fee(message)
            
            # 创建成功响应
            return SMSResponse.success(
                gateway=gateway_name,
                phone_number=to.get_number(),
                message_id=message_id,
                send_time=datetime.now(),
                fee=fee,
                raw_response=response
            )
        except GatewayErrorException as e:
            # 处理网关错误
            return SMSResponse.failed(
                gateway=gateway_name,
                phone_number=to.get_number(),
                error_code=str(e.code),
                error_message=str(e),
                error_details=e.data,
                raw_response=e.data
            )
        except Exception as e:
            # 处理其他异常
            return SMSResponse.failed(
                gateway=gateway_name,
                phone_number=to.get_number(),
                error_code="UNKNOWN_ERROR",
                error_message=str(e),
                raw_response={"error": str(e)}
            )
    
    def _validate_config(self, config: GatewayConfig) -> None:
        """
        验证配置是否有效
        子类可以覆盖此方法实现具体验证逻辑
        
        Args:
            config: 网关配置
            
        Raises:
            ValueError: 配置无效时抛出
        """
        pass
    
    def _get_gateway_name(self) -> str:
        """
        获取网关名称
        
        Returns:
            网关名称
        """
        class_name = self.__class__.__name__
        # 移除Gateway后缀，并转为小写
        if class_name.endswith("Gateway"):
            return class_name[:-7].lower()
        return class_name.lower()
    
    def _extract_message_id(self, response: Dict[str, Any]) -> Optional[str]:
        """
        从响应中提取消息ID
        
        Args:
            response: 网关响应
            
        Returns:
            消息ID，如果不存在返回None
        """
        # 尝试从不同网关的响应中提取消息ID
        for key in ["message_id", "msg_id", "msgid", "smsid", "sid", "id"]:
            if key in response:
                return str(response[key])
        return None
    
    def _calculate_fee(self, message: Message) -> int:
        """
        计算短信计费条数
        
        Args:
            message: 短信消息
            
        Returns:
            计费条数
        """
        # 默认计算逻辑，子类可以覆盖
        content = message.get_content()
        if not content:
            return 1
            
        # 根据内容长度计算条数
        # 普通短信：70个字符一条
        # 长短信：67个字符一条
        length = len(content)
        if length <= 70:
            return 1
        return (length + 66) // 67  # 67个字符一条，向上取整 