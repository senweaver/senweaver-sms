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

class BaiduGateway(BaseGateway):
    """
    百度云网关
    
    通过百度云短信服务发送短信
    """

    endpoint = "https://sms.bj.baidubce.com/api/v3/sendSms"

    def _validate_config(self, config: GatewayConfig) -> None:
        """
        验证配置是否有效
        
        Args:
            config: 网关配置
            
        Raises:
            ValueError: 配置无效时抛出
        """
        if not config.app_id:
            raise ValueError("缺少必要参数: app_id (AccessKeyId)")
        if not config.app_key:
            raise ValueError("缺少必要参数: app_key (AccessKeySecret)")
        if not config.invoke_id:
            raise ValueError("缺少必要参数: invoke_id (调用ID)")

    def _send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """
        使用百度云短信服务发送短信
        
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
        
        # 获取认证头
        headers = self._get_headers(config)
        
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
            
            if result.get("code") != "1000":
                raise GatewayErrorException(
                    result.get("message", "未知错误"),
                    result.get("code", "UNKNOWN_ERROR"),
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
        """从百度云响应中提取请求ID"""
        return response.get("requestId")

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
        # 获取必要的配置值
        template_id = message.get_template(self)
        
        if not template_id:
            raise GatewayErrorException("缺少模板ID", "TEMPLATE_ERROR")
        
        # 格式化手机号
        mobile = to.get_number()
        
        # 获取模板参数
        template_params = message.get_data(self) or {}
        
        # 准备参数
        params = {
            "invokeId": config.invoke_id,
            "phoneNumber": mobile,
            "templateCode": template_id,
        }
        
        # 添加模板参数
        if template_params:
            if isinstance(template_params, list):
                # 如果需要，将列表转换为带索引键的字典
                params_dict = {}
                for i, value in enumerate(template_params):
                    params_dict[f"param{i+1}"] = str(value)
                params["contentVar"] = params_dict
            elif isinstance(template_params, dict):
                params["contentVar"] = {k: str(v) for k, v in template_params.items()}
        
        # 添加签名ID（如果提供）
        if config.signature_id:
            params["signatureId"] = config.signature_id
        
        return params

    def _get_headers(self, config: GatewayConfig) -> Dict[str, str]:
        """
        获取API请求头，包括认证信息
        
        Args:
            config: 网关配置
            
        Returns:
            API请求头
        """
        # 获取凭证
        access_key_id = config.app_id
        access_key_secret = config.app_key
        
        # 基本头信息
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-bce-date": self._get_bce_date()
        }
        
        # 添加授权头
        auth_string = self._get_authorization(headers, access_key_id, access_key_secret)
        headers["Authorization"] = auth_string
        
        return headers

    def _get_bce_date(self) -> str:
        """
        获取BCE日期格式（ISO 8601）
        
        Returns:
            BCE日期字符串
        """
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def _get_authorization(self, headers: Dict[str, str], access_key_id: str, access_key_secret: str) -> str:
        """
        为百度云生成授权头
        
        Args:
            headers: 请求头
            access_key_id: 访问密钥ID
            access_key_secret: 访问密钥密钥
            
        Returns:
            授权字符串
        """
        # 创建规范请求
        canonical_uri = "/api/v3/sendSms"
        canonical_query_string = ""
        
        # 创建规范头
        canonical_headers = ""
        signed_headers = []
        
        for key in sorted(headers.keys()):
            lower_key = key.lower()
            signed_headers.append(lower_key)
            canonical_headers += f"{lower_key}:{headers[key]}\n"
        
        # 连接已签名的头
        signed_headers_str = ";".join(signed_headers)
        
        # 创建待签名字符串
        string_to_sign = f"POST\n{canonical_uri}\n{canonical_query_string}\n{canonical_headers}"
        
        # 生成签名
        signature = hmac.new(
            access_key_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # 创建授权字符串
        return f"bce-auth-v1/{access_key_id}/{self._get_bce_date().split('T')[0]}/{signed_headers_str}/{signature}" 