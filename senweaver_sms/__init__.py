"""
SenWeaver-SMS - 强大、灵活且易用的短信发送组件
"""

from .phone_number import PhoneNumber
from .message import Message
from .config import SMSConfig, GatewayConfig
from .request import SMSRequest
from .response import SMSResponse, SMSBatchResponse, SMSStatus, SMSError
from .builder import SMSBuilder

__version__ = "0.1.2"
__author__ = "senweaver"

__all__ = [
    "PhoneNumber",    # 手机号封装类
    "Message",        # 短信消息类
    "SMSConfig",      # 短信配置类
    "GatewayConfig",  # 网关配置类
    "SMSRequest",     # 短信请求类
    "SMSResponse",    # 短信响应类
    "SMSBatchResponse", # 批量短信响应类
    "SMSStatus",      # 短信状态枚举
    "SMSError",       # 短信错误信息类
    "SMSBuilder"      # 短信构建器类
] 