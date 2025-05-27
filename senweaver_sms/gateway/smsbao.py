"""
短信宝网关 - 通过短信宝服务发送短信
"""
import hashlib
import requests
from typing import Dict, Any

from ..phone_number import PhoneNumber
from ..message import Message
from ..exception.exception import GatewayErrorException
from ..config import GatewayConfig
from .base import BaseGateway


class SmsBaoGateway(BaseGateway):
    """
    短信宝网关
    
    通过短信宝(smsbao.com)服务发送短信
    """
    # 接口地址
    endpoint = "http://api.smsbao.com/sms"

    # 状态码映射
    STATUS_CODES = {
        "0": "发送成功",
        "30": "密码错误",
        "40": "账号不存在",
        "41": "余额不足",
        "42": "账号过期",
        "43": "IP地址受限",
        "50": "内容含有敏感词",
        "51": "手机号码不正确",
        "60": "发送频率过快",
        "70": "时间段限制",
        "80": "内容超出长度限制",
    }

    def _validate_config(self, config: GatewayConfig) -> None:
        """
        验证配置是否有效
        
        Args:
            config: 网关配置
            
        Raises:
            ValueError: 配置无效时抛出
        """
        if not config.app_id:
            raise ValueError("短信宝用户名不能为空，请设置app_id")
        if not config.app_key:
            raise ValueError("短信宝密码不能为空，请设置app_key")

    def _send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """
        发送短信
        
        Args:
            to: 接收人手机号
            message: 短信消息
            config: 网关配置
            
        Returns:
            网关响应
            
        Raises:
            GatewayErrorException: 发送失败时抛出
        """
        # 准备参数
        params = self._get_params(to, message, config)
        
        # 发送请求
        try:
            response = requests.get(
                self.endpoint,
                params=params,
                timeout=config.timeout
            )
            
            response.raise_for_status()
            status_code = response.text.strip()
            
            # 短信宝只返回一个状态码
            if status_code != "0":
                error_message = self.STATUS_CODES.get(status_code, "未知错误")
                raise GatewayErrorException(
                    error_message,
                    status_code,
                    {"status": status_code, "message": error_message}
                )
            
            return {
                "status": "0",
                "message": "发送成功",
                "mobile": to.get_number()
            }
        except requests.exceptions.RequestException as e:
            raise GatewayErrorException(str(e), "REQUEST_ERROR", e)
        except Exception as e:
            if isinstance(e, GatewayErrorException):
                raise e
            raise GatewayErrorException(str(e), "UNKNOWN_ERROR", e)

    def _get_params(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, str]:
        """
        获取API请求参数
        
        Args:
            to: 接收人手机号
            message: 短信消息
            config: 网关配置
            
        Returns:
            请求参数字典
        """
        # 获取短信内容
        content = message.get_content()
        if not content:
            raise GatewayErrorException("短信内容不能为空", "CONTENT_ERROR")
        
        # 添加签名
        if config.sign and not content.startswith(f"【{config.sign}】"):
            content = f"【{config.sign}】{content}"
        
        # 获取手机号
        phone_number = to.get_number()
        
        # 密码MD5加密 
        # 短信宝使用app_id作为用户名，app_key作为密码
        username = config.app_id
        password = config.app_key
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        
        return {
            "u": username,
            "p": hashed_password,
            "m": phone_number,
            "c": content,
        } 