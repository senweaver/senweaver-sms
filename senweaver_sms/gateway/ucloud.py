import json
import requests
import hashlib
from typing import Dict, Any, Optional

from ..phone_number import PhoneNumber
from ..message import Message
from ..exception.exception import GatewayErrorException
from ..config import GatewayConfig
from .base import BaseGateway

class UcloudGateway(BaseGateway):
    """
    UCloud短信网关
    
    通过UCloud短信服务发送短信
    """

    endpoint = "https://api.ucloud.cn"

    def _validate_config(self, config: GatewayConfig) -> None:
        """
        验证配置是否有效
        
        Args:
            config: 网关配置
            
        Raises:
            ValueError: 配置无效时抛出
        """
        if not config.app_id:
            raise ValueError("缺少必要参数: app_id (UCloud PublicKey)")
        if not config.app_key:
            raise ValueError("缺少必要参数: app_key (UCloud PrivateKey)")
        if not config.sign:
            raise ValueError("缺少必要参数: sign (短信签名)")

    def _send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """
        使用UCloud短信服务发送短信
        
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
        params = self._sign_params(params, config)
        
        # 发送请求
        try:
            # 设置头信息
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            
            # 发送请求
            response = requests.post(
                self.endpoint,
                data=params,
                headers=headers,
                timeout=config.timeout,
                verify=config.ssl_verify
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("RetCode") != 0:
                raise GatewayErrorException(
                    result.get("Message", "未知错误"),
                    result.get("RetCode", "UNKNOWN_ERROR"),
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
        """从UCloud响应中提取消息ID (SessionNo)"""
        return response.get("SessionNo")

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
        # 获取模板ID
        template_id = message.get_template(self)
        if not template_id:
            raise GatewayErrorException("缺少模板ID", "TEMPLATE_ERROR")
        
        # 准备参数
        params = {
            "Action": "SendUSMSMessage",
            "PublicKey": config.app_id,
            "SigContent": config.sign,
            "TemplateId": template_id,
        }
        
        # 添加项目ID（如果指定）
        if config.project_id:
            params["ProjectId"] = config.project_id
        
        # 获取手机号
        phone_numbers = to.get_number()
        params["PhoneNumbers"] = phone_numbers
        
        # 获取模板参数
        template_params = message.get_data(self)
        if template_params:
            # 格式化模板参数
            if isinstance(template_params, dict):
                # 转换为列表
                template_params = list(template_params.values())
            
            # 转换为JSON字符串
            params["TemplateParams"] = json.dumps(template_params)
        
        return params

    def _sign_params(self, params: Dict[str, str], config: GatewayConfig) -> Dict[str, str]:
        """
        使用私钥对参数进行签名
        
        Args:
            params: 要签名的参数
            config: 网关配置
            
        Returns:
            已签名的参数
        """
        # 获取私钥
        private_key = config.app_key
        
        # 排序参数
        sorted_params = sorted(params.items())
        
        # 构建查询字符串
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # 添加私钥
        string_to_sign = query_string + private_key
        
        # 生成签名
        signature = hashlib.sha1(string_to_sign.encode('utf-8')).hexdigest()
        
        # 将签名添加到参数中
        params["Signature"] = signature
        
        return params 