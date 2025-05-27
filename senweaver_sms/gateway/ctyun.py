import json
import time
import hmac
import hashlib
import requests
from typing import Dict, Any, Optional

from ..phone_number import PhoneNumber
from ..message import Message
from ..exception.exception import GatewayErrorException
from ..config import GatewayConfig
from .base import BaseGateway

class CtyunGateway(BaseGateway):
    """
    天翼云网关 (China Telecom E-Surfing Cloud)
    
    通过天翼云短信服务发送短信
    """

    endpoint = "https://api.ctyun.cn/sms/api/v1/send/sms"

    def _validate_config(self, config: GatewayConfig) -> None:
        """
        验证配置是否有效
        
        Args:
            config: 网关配置
            
        Raises:
            ValueError: 配置无效时抛出
        """
        if not config.app_id:
            raise ValueError("缺少必要参数: app_id (天翼云AccessKey)")
        if not config.app_key:
            raise ValueError("缺少必要参数: app_key (天翼云SecretKey)")
        if not config.sign:
            raise ValueError("缺少必要参数: sign (短信签名)")

    def _send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """
        使用天翼云短信服务发送短信
        
        Args:
            to: 接收人手机号
            message: 短信消息
            config: 网关配置
            
        Raises:
            GatewayErrorException: 发送失败时抛出
            
        Returns:
            网关原始响应
        """
        # 准备参数
        params = self._get_params(to, message, config)
        request_body = json.dumps(params).encode('utf-8')
        
        # 生成头信息
        headers = self._get_headers(request_body, config)
        
        # 发送请求
        try:
            # 使用requests发送请求
            response = requests.post(
                self.endpoint,
                json=params,
                headers=headers,
                timeout=config.timeout,
                verify=config.ssl_verify
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("statusCode") != "200":
                raise GatewayErrorException(
                    result.get("reason", "未知错误"),
                    result.get("statusCode", "UNKNOWN_ERROR"),
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
        """从天翼云响应中提取请求ID"""
        # 天翼云的成功响应结构可能嵌套，例如在 result 或 data 中
        if response.get("result") and isinstance(response["result"], dict):
            return response["result"].get("requestId")
        return response.get("requestId") # 直接尝试顶层

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
        # 获取模板ID
        template_id = message.get_template(self)
        if not template_id:
            raise GatewayErrorException("缺少模板ID", "TEMPLATE_ERROR")
        
        # 格式化手机号
        phone_number = to.get_number()
        
        # 获取模板参数
        template_params = message.get_data(self) or {}
        
        # 准备参数
        return {
            "sign": config.sign,
            "templateCode": template_id,
            "phoneNumbers": phone_number,
            "templateParam": json.dumps(template_params) if template_params else "{}"
        }

    def _get_headers(self, body: bytes, config: GatewayConfig) -> Dict[str, str]:
        """
        获取API请求头，包括认证信息
        
        Args:
            body: 请求体
            config: 网关配置
            
        Returns:
            API请求头
        """
        # 获取凭证
        access_key = config.app_id
        secret_key = config.app_key
        
        # 获取时间戳
        now = int(time.time() * 1000)
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime(now / 1000))
        
        # 计算内容SHA256
        content_sha256 = hashlib.sha256(body).hexdigest()
        
        # 生成签名
        string_to_sign = f"ctyun;{access_key};{timestamp};{content_sha256}"
        signature = hmac.new(
            secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # 创建授权头
        auth_header = f"ctyun {access_key}:{timestamp}:{signature}"
        
        return {
            "Content-Type": "application/json;charset=utf-8",
            "eop-date": timestamp,
            "eop-content-sha256": content_sha256,
            "Authorization": auth_header,
        } 