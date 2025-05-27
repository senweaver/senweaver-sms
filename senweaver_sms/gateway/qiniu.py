import json
import hmac
import hashlib
import base64
import requests
from typing import Dict, Any, Optional

from ..phone_number import PhoneNumber
from ..message import Message
from ..exception.exception import GatewayErrorException
from ..config import GatewayConfig
from .base import BaseGateway

class QiniuGateway(BaseGateway):
    """
    七牛云短信网关
    
    通过七牛云短信服务发送短信
    """

    endpoint = "https://sms.qiniuapi.com/v1/message"

    def _validate_config(self, config: GatewayConfig) -> None:
        """
        验证配置是否有效
        
        Args:
            config: 网关配置
            
        Raises:
            ValueError: 配置无效时抛出
        """
        if not config.app_id:
            raise ValueError("缺少必要参数: app_id (七牛AccessKey)")
        if not config.app_key:
            raise ValueError("缺少必要参数: app_key (七牛SecretKey)")

    def _send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """
        使用七牛云短信服务发送短信
        
        Args:
            to: 接收人手机号
            message: 短信消息
            config: 网关配置
            
        Raises:
            GatewayErrorException: 发送失败时抛出
            
        Returns:
            网关原始响应
        """
        # 获取请求体
        body = self._get_request_body(to, message, config)
        request_body = json.dumps(body).encode('utf-8')
        
        # 生成授权头
        headers = {
            "Content-Type": "application/json",
            "Authorization": self._generate_auth_token(config.app_id, config.app_key, self.endpoint, request_body)
        }
        
        # 发送请求
        try:
            response = requests.post(
                self.endpoint,
                json=body,
                headers=headers,
                timeout=config.timeout,
                verify=config.ssl_verify
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise GatewayErrorException(
                    result.get("message", "未知错误"),
                    result.get("error", "UNKNOWN_ERROR"),
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
        """从七牛云响应中提取消息ID (job_id)"""
        return response.get("job_id")

    def _get_request_body(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """
        获取API请求的请求体
        
        Args:
            to: 接收人手机号
            message: 短信消息
            config: 网关配置
            
        Returns:
            API请求的请求体
        """
        # 获取模板ID
        template_id = message.get_template(self)
        if not template_id:
            raise GatewayErrorException("缺少模板ID", "TEMPLATE_ERROR")
        
        # 格式化手机号
        mobile = to.get_number()
        
        # 获取模板参数
        template_params = message.get_data(self) or {}
        
        return {
            "template_id": template_id,
            "mobile": mobile,
            "parameters": template_params,
        }

    def _generate_auth_token(self, access_key: str, secret_key: str, url: str, body: bytes) -> str:
        """
        生成七牛授权令牌
        
        Args:
            access_key: 访问密钥
            secret_key: 密钥
            url: 请求URL
            body: 请求体
            
        Returns:
            授权令牌
        """
        # 解析URL
        parsed_url = requests.utils.urlparse(url)
        
        # 创建待签名字符串
        path = parsed_url.path
        if parsed_url.query:
            path = f"{path}?{parsed_url.query}"
        
        data_to_sign = f"POST {path}\nHost: {parsed_url.netloc}\nContent-Type: application/json\n\n"
        
        if body:
            data_to_sign += body.decode('utf-8')
        
        # 生成签名
        signature = hmac.new(
            secret_key.encode('utf-8'),
            data_to_sign.encode('utf-8'),
            hashlib.sha1
        ).digest()
        
        encoded_signature = base64.urlsafe_b64encode(signature).decode('utf-8')
        
        # 生成令牌
        return f"Qiniu {access_key}:{encoded_signature}" 