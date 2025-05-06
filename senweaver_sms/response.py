"""
短信响应类 - 统一的短信发送结果
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List, Union
from datetime import datetime


class SMSStatus(Enum):
    """
    短信状态枚举
    """
    SUCCESS = "success"      # 发送成功
    FAILED = "failed"        # 发送失败
    PENDING = "pending"      # 待发送
    DELIVERING = "delivering"  # 发送中
    REJECTED = "rejected"    # 被拒绝
    UNKNOWN = "unknown"      # 未知状态


@dataclass
class SMSError:
    """
    短信错误信息
    """
    code: str                # 错误代码
    message: str             # 错误消息
    details: Optional[Dict[str, Any]] = field(default_factory=dict)  # 详细错误信息

    def __str__(self) -> str:
        return f"{self.message} (错误代码: {self.code})"


@dataclass
class SMSResponse:
    """
    短信响应类
    用于统一处理和表示短信发送结果
    """
    # 基本信息
    gateway: str                                   # 网关名称
    status: SMSStatus                              # 发送状态
    phone_number: str                              # 手机号码
    
    # 成功信息
    message_id: Optional[str] = None               # 消息ID
    send_time: Optional[datetime] = None           # 发送时间
    fee: Optional[int] = None                      # 计费条数
    
    # 错误信息
    error: Optional[SMSError] = None               # 错误信息
    
    # 原始信息
    raw_response: Dict[str, Any] = field(default_factory=dict)   # 原始响应
    
    @property
    def is_success(self) -> bool:
        """
        是否发送成功
        
        Returns:
            是否成功
        """
        return self.status == SMSStatus.SUCCESS
    
    @property
    def is_failed(self) -> bool:
        """
        是否发送失败
        
        Returns:
            是否失败
        """
        return self.status == SMSStatus.FAILED
    
    @classmethod
    def success(cls, 
                gateway: str, 
                phone_number: str, 
                message_id: Optional[str] = None, 
                send_time: Optional[datetime] = None,
                fee: Optional[int] = None,
                raw_response: Optional[Dict[str, Any]] = None) -> 'SMSResponse':
        """
        创建成功响应
        
        Args:
            gateway: 网关名称
            phone_number: 手机号码
            message_id: 消息ID
            send_time: 发送时间
            fee: 计费条数
            raw_response: 原始响应
            
        Returns:
            成功响应对象
        """
        return cls(
            gateway=gateway,
            status=SMSStatus.SUCCESS,
            phone_number=phone_number,
            message_id=message_id,
            send_time=send_time or datetime.now(),
            fee=fee,
            raw_response=raw_response or {}
        )
    
    @classmethod
    def failed(cls, 
               gateway: str, 
               phone_number: str, 
               error_code: str,
               error_message: str,
               error_details: Optional[Dict[str, Any]] = None,
               raw_response: Optional[Dict[str, Any]] = None) -> 'SMSResponse':
        """
        创建失败响应
        
        Args:
            gateway: 网关名称
            phone_number: 手机号码
            error_code: 错误代码
            error_message: 错误消息
            error_details: 错误详情
            raw_response: 原始响应
            
        Returns:
            失败响应对象
        """
        return cls(
            gateway=gateway,
            status=SMSStatus.FAILED,
            phone_number=phone_number,
            error=SMSError(
                code=error_code,
                message=error_message,
                details=error_details or {}
            ),
            raw_response=raw_response or {}
        )
    
    def __str__(self) -> str:
        """
        字符串表示
        
        Returns:
            对象的字符串表示
        """
        if self.is_success:
            return f"短信发送成功 [网关: {self.gateway}] [手机号: {self.phone_number}] [消息ID: {self.message_id or '未知'}]"
        else:
            error_msg = f"{self.error.message} (代码: {self.error.code})" if self.error else "未知错误"
            return f"短信发送失败 [网关: {self.gateway}] [手机号: {self.phone_number}] [错误: {error_msg}]"


@dataclass
class SMSBatchResponse:
    """
    批量短信响应类
    用于处理多个接收人或多个网关的发送结果
    """
    responses: List[SMSResponse] = field(default_factory=list)
    
    @property
    def is_success(self) -> bool:
        """
        是否所有短信都发送成功
        
        Returns:
            是否全部成功
        """
        if not self.responses:
            return False
        return all(response.is_success for response in self.responses)
    
    @property
    def is_failed(self) -> bool:
        """
        是否有短信发送失败
        
        Returns:
            是否有失败
        """
        return not self.is_success
    
    def add_response(self, response: SMSResponse) -> None:
        """
        添加响应
        
        Args:
            response: 短信响应对象
        """
        self.responses.append(response)
    
    def get_success_responses(self) -> List[SMSResponse]:
        """
        获取所有成功的响应
        
        Returns:
            成功的响应列表
        """
        return [response for response in self.responses if response.is_success]
    
    def get_failed_responses(self) -> List[SMSResponse]:
        """
        获取所有失败的响应
        
        Returns:
            失败的响应列表
        """
        return [response for response in self.responses if response.is_failed]
        
    def get_gateway_responses(self, gateway: str) -> List[SMSResponse]:
        """
        获取指定网关的响应
        
        Args:
            gateway: 网关名称
            
        Returns:
            指定网关的响应列表
        """
        return [response for response in self.responses if response.gateway == gateway]
        
    def __str__(self) -> str:
        """
        字符串表示
        
        Returns:
            对象的字符串表示
        """
        success_count = len(self.get_success_responses())
        failed_count = len(self.get_failed_responses())
        return f"批量短信发送结果 [成功: {success_count}] [失败: {failed_count}] [总计: {len(self.responses)}]" 