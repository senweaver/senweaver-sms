import json
import hmac
import uuid
import base64
import datetime
import requests
from hashlib import sha1
from typing import Dict, Any, Optional

from ..phone_number import PhoneNumber
from ..message import Message
from ..exception.exception import GatewayErrorException
from ..config import GatewayConfig
from .base import BaseGateway

class AliyunGateway(BaseGateway):
    """
    阿里云短信网关
    
    通过阿里云SMS服务发送短信
    """

    endpoint = "https://dysmsapi.aliyuncs.com"
    signature_method = "HMAC-SHA1"
    signature_version = "1.0"
    format = "JSON"
    version = "2017-05-25"

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
        if not config.sign:
            raise ValueError("缺少必要参数: sign (SignName)")

    def _send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """
        使用阿里云SMS服务发送短信
        
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
        
        # 添加签名
        params["Signature"] = self._generate_signature(params, config.app_key)
        
        # 构建请求URL
        try:
            response = requests.get(
                self.endpoint,
                params=params,
                timeout=config.timeout,
                verify=config.ssl_verify
            )
            response.raise_for_status()  # 抛出异常如果状态码不是200
            result = response.json()
            
            if result["Code"] != "OK":
                raise GatewayErrorException(
                    result.get("Message", "Unknown error"),
                    result.get("Code"),
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
        """从阿里云响应中提取消息ID (BizId)"""
        return response.get("BizId")

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
        params = {
            "AccessKeyId": config.app_id,
            "Action": "SendSms",
            "Format": self.format,
            "PhoneNumbers": to.get_number(),
            "RegionId": config.region or "cn-hangzhou",
            "SignName": config.sign,
            "SignatureMethod": self.signature_method,
            "SignatureNonce": str(uuid.uuid4()),
            "SignatureVersion": self.signature_version,
            "TemplateCode": message.get_template(self),
            "Timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "Version": config.version or self.version,
        }
        
        # 添加模板参数
        template_param = message.get_data(self)
        if template_param:
            params["TemplateParam"] = json.dumps(template_param, ensure_ascii=False)

        # 国际短信使用国家代码
        country_code = to.get_country_code()
        if country_code and country_code != "86":
            # 仅对非中国号码添加
            params["SmsUpExtendCode"] = country_code
        
        return params

    def _generate_signature(self, params: Dict[str, Any], secret: str) -> str:
        """
        生成API请求签名
        
        Args:
            params: API请求参数
            secret: AccessKey密钥
            
        Returns:
            签名
        """
        # 排序参数
        sorted_params = sorted(params.items())
        
        # 构建规范化查询字符串
        canonicalized_query_string = "&".join([
            f"{requests.utils.quote(k)}={requests.utils.quote(str(v))}"
            for k, v in sorted_params
        ])
        
        # 构建待签名字符串
        string_to_sign = "GET&%2F&" + requests.utils.quote(canonicalized_query_string)
        
        # 计算HMAC-SHA1
        secret_bytes = (secret + "&").encode("utf-8")
        string_to_sign_bytes = string_to_sign.encode("utf-8")
        signature = base64.b64encode(
            hmac.new(secret_bytes, string_to_sign_bytes, sha1).digest()
        ).decode("utf-8")
        
        return signature 