import requests
from typing import Dict, Any, Optional

from ..phone_number import PhoneNumber
from ..message import Message
from ..exception.exception import GatewayErrorException
from ..config import GatewayConfig
from .base import BaseGateway

class YunpianGateway(BaseGateway):
    """
    云片短信网关
    
    通过云片SMS服务发送短信
    """

    endpoint = "https://sms.yunpian.com/v2/sms/single_send.json"

    def _validate_config(self, config: GatewayConfig) -> None:
        """
        验证配置是否有效
        
        Args:
            config: 网关配置
            
        Raises:
            ValueError: 配置无效时抛出
        """
        if not config.app_key:
            raise ValueError("缺少必要参数: app_key (API Key)")

    def _send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """
        使用云片SMS服务发送短信
        
        Args:
            to: 接收人手机号
            message: 短信消息
            config: 网关配置
            
        Raises:
            GatewayErrorException: 发送失败时抛出
            
        Returns:
            网关原始响应
        """
        params = self._get_params(to, message, config)
        
        # 发送请求
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
            response = requests.post(
                self.endpoint,
                data=params,
                headers=headers,
                timeout=config.timeout,
                verify=config.ssl_verify
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") != 0:
                raise GatewayErrorException(
                    result.get("msg", "Unknown error"),
                    result.get("code"),
                    result
                )
            
            return result
        except requests.exceptions.RequestException as e:
            raise GatewayErrorException(str(e), "REQUEST_ERROR", e)
        except Exception as e:
            if isinstance(e, GatewayErrorException):
                raise e
            raise GatewayErrorException(str(e), "UNKNOWN_ERROR", e)

    def _extract_message_id(self, response: Dict[str, Any]) -> Optional[str]:
        """从云片响应中提取消息ID (sid)"""
        return response.get("sid")

    def _get_params(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """
        获取API请求参数
        
        Args:
            to: 接收人手机号
            message: 短信消息
            config: 网关配置
            
        Returns:
            API请求参数
        """
        # 获取内容
        content = message.get_content(self)
        if not content:
            raise GatewayErrorException("云片网关缺少短信内容")
        
        # 检查内容是否有签名
        signature = config.sign or config.extras.get("signature", "")
        if signature and not content.startswith(f"【{signature}】"):
            # 如果没有签名，添加签名
            content = f"【{signature}】{content}"
        
        # 构建手机号
        mobile = to.get_number()
        country_code = to.get_country_code()
        if country_code and country_code != "86":
            # 国际短信
            mobile = f"+{country_code}{mobile}"
        
        return {
            "apikey": config.app_key,
            "mobile": mobile,
            "text": content,
        } 