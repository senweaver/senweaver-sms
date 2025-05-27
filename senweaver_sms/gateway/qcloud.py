import json
import hashlib
import hmac
import time
import requests
from typing import Dict, Any, Optional

from ..phone_number import PhoneNumber
from ..message import Message
from ..exception.exception import GatewayErrorException
from ..config import GatewayConfig
from .base import BaseGateway

class QcloudGateway(BaseGateway):
    """
    腾讯云网关 (Tencent Cloud SMS)
    
    通过腾讯云短信服务发送短信
    """

    url = "https://sms.tencentcloudapi.com"
    host = "sms.tencentcloudapi.com"
    service = "sms"
    version = "2021-01-11"

    def _validate_config(self, config: GatewayConfig) -> None:
        """
        验证配置是否有效
        
        Args:
            config: 网关配置
            
        Raises:
            ValueError: 配置无效时抛出
        """
        if not config.app_id:
            raise ValueError("缺少必要参数: app_id (SDK App ID)")
        if not config.app_key:
            raise ValueError("缺少必要参数: app_key (Secret ID)")
        if not config.app_secret:
            raise ValueError("缺少必要参数: app_secret (Secret Key)")
        if not config.sign:
            raise ValueError("缺少必要参数: sign (短信签名)")

    def _send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """
        使用腾讯云短信服务发送短信
        
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
        
        # 获取认证参数
        auth_params = self._get_auth_params(params, config)
        
        # 请求头
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Host": self.host,
            "X-TC-Action": "SendSms",
            "X-TC-Timestamp": str(int(time.time())),
            "X-TC-Version": config.version or self.version,
            "X-TC-Region": config.region or "",
            "Authorization": auth_params["authorization"],
        }
        
        # 发送请求
        try:
            response = requests.post(
                self.url,
                json=params,
                headers=headers,
                timeout=config.timeout,
                verify=config.ssl_verify
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "Error" in result.get("Response", {}):
                error = result["Response"]["Error"]
                raise GatewayErrorException(
                    error.get("Message", "未知错误"),
                    error.get("Code", "UNKNOWN_ERROR"),
                    result
                )
            
            return result["Response"]
        except requests.exceptions.RequestException as e:
            raise GatewayErrorException(str(e), "REQUEST_ERROR", e)
        except Exception as e:
            if isinstance(e, GatewayErrorException):
                raise e
            raise GatewayErrorException(str(e), "UNKNOWN_ERROR", e)

    def _extract_message_id(self, response: Dict[str, Any]) -> Optional[str]:
        """从腾讯云响应中提取消息ID (SerialNo)"""
        status_set = response.get("SendStatusSet")
        if isinstance(status_set, list) and status_set:
            first_status = status_set[0]
            if isinstance(first_status, dict):
                return first_status.get("SerialNo")
        return None

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
        template_id = message.get_template(self)
        if not template_id:
            raise GatewayErrorException("缺少模板ID", "TEMPLATE_ERROR")
        
        # 格式化手机号
        phone_number = f"+{to.get_country_code() or '86'}{to.get_number()}"
        
        # 获取模板参数
        template_param_set = []
        template_params = message.get_data(self)
        if isinstance(template_params, list):
            template_param_set = template_params
        elif isinstance(template_params, dict):
            # 对字典值进行排序（腾讯云期望参数按顺序）
            template_param_set = list(template_params.values())
        
        return {
            "PhoneNumberSet": [phone_number],
            "SmsSdkAppId": str(config.app_id),
            "SignName": config.sign,
            "TemplateId": str(template_id),
            "TemplateParamSet": [str(param) for param in template_param_set],
        }

    def _get_auth_params(self, params: Dict[str, Any], config: GatewayConfig) -> Dict[str, Any]:
        """
        生成API请求的认证参数
        
        Args:
            params: API请求参数
            config: 网关配置
            
        Returns:
            认证参数
        """
        secret_id = config.app_key
        secret_key = config.app_secret
        
        # 获取时间戳和日期
        timestamp = int(time.time())
        date = time.strftime("%Y-%m-%d", time.gmtime(timestamp))
        
        # 生成规范请求字符串
        http_request_method = "POST"
        canonical_uri = "/"
        canonical_query_string = ""
        canonical_headers = f"content-type:application/json; charset=utf-8\nhost:{self.host}\n"
        signed_headers = "content-type;host"
        hashed_request_payload = hashlib.sha256(json.dumps(params).encode("utf-8")).hexdigest()
        canonical_request = f"{http_request_method}\n{canonical_uri}\n{canonical_query_string}\n{canonical_headers}\n{signed_headers}\n{hashed_request_payload}"
        
        # 生成待签名字符串
        algorithm = "TC3-HMAC-SHA256"
        credential_scope = f"{date}/{self.service}/tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = f"{algorithm}\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}"
        
        # 计算签名
        secret_date = self._hmac_sha256(f"TC3{secret_key}".encode("utf-8"), date)
        secret_service = self._hmac_sha256(secret_date, self.service)
        secret_signing = self._hmac_sha256(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
        
        # 生成授权信息
        authorization = (
            f"{algorithm} "
            f"Credential={secret_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        
        return {
            "authorization": authorization,
            "timestamp": timestamp,
            "date": date,
        }

    def _hmac_sha256(self, key: bytes, msg: str) -> bytes:
        """
        计算HMAC-SHA256
        
        Args:
            key: 密钥
            msg: 消息
            
        Returns:
            HMAC-SHA256结果
        """
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest() 