"""华为云短信网关实现"""
import json
import time
import random
import hashlib
import requests
from typing import Dict, Any, Optional

from ..phone_number import PhoneNumber
from ..message import Message
from ..exception.exception import GatewayErrorException
from ..config import GatewayConfig
from .base import BaseGateway


class HuaweiGateway(BaseGateway):
    """华为云短信网关
    
    通过华为云短信服务发送短信
    必要配置:
        - app_id: 应用ID/APP KEY
        - app_key: 应用密钥/APP SECRET
        - channel: 短信通道号 (sender)
        - sign: 短信签名 (可选, 如果未提供则尝试使用 channel)
        - endpoint: API接入地址 (可选, 默认中国区)
    """

    # 默认端点
    default_endpoint = "https://smsapi.cn-north-4.myhuaweicloud.com"
    api_path = "/sms/batchSendSms/v1"

    def _validate_config(self, config: GatewayConfig) -> None:
        """
        验证配置是否有效
        
        Args:
            config: 网关配置
            
        Raises:
            ValueError: 配置无效时抛出
        """
        if not config.app_id:
            raise ValueError("缺少必要参数: app_id (APP KEY)")
        if not config.app_key:
            raise ValueError("缺少必要参数: app_key (APP SECRET)")
        if not config.channel:
            raise ValueError("缺少必要参数: channel (短信通道号)")

    def _send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """使用华为云短信服务发送短信

        Args:
            to: 接收人手机号
            message: 短信消息
            config: 网关配置

        Raises:
            GatewayErrorException: 发送失败时抛出

        Returns:
            网关原始响应
        """
        # 构建请求体
        body = {
            "from": config.channel,
            "to": [to.get_number()],
            "templateId": message.get_template(self),
            "signature": config.sign or config.channel,  # 默认使用channel作为签名
            "statusCallback": config.callback_url or "",
        }

        # 添加模板参数
        template_param = message.get_data(self)
        if template_param:
            body["templateParas"] = json.dumps(template_param, ensure_ascii=False)

        try:
            # 准备请求
            endpoint_url = config.endpoint or self.default_endpoint
            url = f"{endpoint_url}{self.api_path}"
            headers = {
                "Content-Type": "application/json",
                **self._get_auth_headers(config.app_id, config.app_key)
            }
            
            # 使用requests发送请求
            response = requests.post(
                url,
                json=body,
                headers=headers,
                timeout=config.timeout,
                verify=config.ssl_verify
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") != "000000":
                raise GatewayErrorException(
                    result.get("description", "未知错误"),
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
        """从华为云响应中提取消息ID (smsMsgId)"""
        result_list = response.get("result")
        if isinstance(result_list, list) and result_list:
            first_result = result_list[0]
            if isinstance(first_result, dict):
                return first_result.get("smsMsgId")
        return None

    def _get_auth_headers(self, app_key: str, app_secret: str) -> Dict[str, str]:
        """生成认证头信息

        Args:
            app_key: 应用密钥
            app_secret: 应用密钥

        Returns:
            认证头信息
        """
        timestamp = str(int(time.time() * 1000))
        nonce = str(random.randint(100000, 999999))
        
        # 生成签名
        sign_str = f"{app_secret}{nonce}{timestamp}"
        signature = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
        
        return {
            "X-App-Key": app_key,
            "X-Nonce": nonce,
            "X-Timestamp": timestamp,
            "X-Signature": signature,
        }

    def query_status(self, task_id: str, config: GatewayConfig) -> Dict[str, Any]:
        """查询已发送短信的状态

        Args:
            task_id: 发送操作返回的任务ID
            config: 网关配置

        Raises:
            GatewayErrorException: 查询失败时抛出

        Returns:
            查询结果
        """
        try:
            endpoint_url = config.endpoint or self.default_endpoint
            url = f"{endpoint_url}/sms/getSmsTaskDetail/v1"
            headers = {
                "Content-Type": "application/json",
                **self._get_auth_headers(config.app_id, config.app_key)
            }
            
            # 使用requests发送请求
            response = requests.post(
                url,
                json={"taskId": task_id},
                headers=headers,
                timeout=config.timeout,
                verify=config.ssl_verify
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") != "000000":
                raise GatewayErrorException(
                    result.get("description", "未知错误"),
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