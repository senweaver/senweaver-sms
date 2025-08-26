"""移动mas短信网关实现"""
import json
import base64
import hashlib
import requests
from typing import Dict, Any, Optional

from ..phone_number import PhoneNumber
from ..message import Message
from ..exception.exception import GatewayErrorException
from ..config import GatewayConfig
from .base import BaseGateway


class MasGateway(BaseGateway):
    """移动mas短信网关
    
    通过中国移动云MAS平台发送短信
    必要配置:
        - app_id: 用户名/账号 (apId)
        - app_key: 用户密码 (secretKey)
        - app_secret: 企业名称 (ecName)
        - sign: 签名编码
        - endpoint: API接入地址 (可选, 默认普通短信接口)
    """

    # 默认端点
    default_endpoint = "http://112.35.1.155:1992/sms/norsubmit"
    template_endpoint = "http://112.35.1.155:1992/sms/tmpsubmit"

    def _validate_config(self, config: GatewayConfig) -> None:
        """验证配置是否有效
        
        Args:
            config: 网关配置
            
        Raises:
            ValueError: 配置无效时抛出
        """
        # 验证必需的配置参数
        required_fields = ['app_id', 'app_key', 'app_secret', 'sign']
        for field in required_fields:
            if not getattr(config, field):
                raise ValueError(f"MAS网关缺少必需的配置参数: {field}")
        
        # app_secret存储ec_name（企业代码）
        if not config.app_secret:
            raise ValueError("MAS网关缺少必需的配置参数: ec_name (app_secret)")

    def _send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """使用移动mas短信服务发送短信

        Args:
            to: 接收人手机号
            message: 短信消息
            config: 网关配置

        Raises:
            GatewayErrorException: 发送失败时抛出

        Returns:
            网关原始响应
        """
        # 判断是否为模板短信
        template_id = message.get_template(self)
        if template_id:
            return self._send_template_sms(to, message, config)
        else:
            return self._send_normal_sms(to, message, config)

    def _send_normal_sms(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """发送普通短信
        
        Args:
            to: 接收人手机号
            message: 短信消息
            config: 网关配置
            
        Returns:
            网关原始响应
        """
        # 构建请求参数
        add_serial = getattr(config, 'add_serial', '') or ''  # 扩展码，默认为空
        
        request_data = {
            "ecName": config.app_secret,  # 企业名称（存储在app_secret中）
            "apId": config.app_id,        # 用户名/账号
            "mobiles": to.get_number(),   # 手机号码
            "content": message.get_content(self),  # 短信内容
            "sign": config.sign,          # 签名编码
            "addSerial": add_serial       # 扩展码
        }
        
        # 生成MAC签名
        mac_string = (
            request_data["ecName"] +
            request_data["apId"] +
            config.app_key +
            request_data["mobiles"] +
            request_data["content"] +
            request_data["sign"] +
            request_data["addSerial"]
        )
        request_data["mac"] = hashlib.md5(mac_string.encode('utf-8')).hexdigest().lower()
        
        return self._make_request(request_data, config, is_template=False)

    def _send_template_sms(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """发送模板短信
        
        Args:
            to: 接收人手机号
            message: 短信消息
            config: 网关配置
            
        Returns:
            网关原始响应
        """
        # 构建请求参数
        add_serial = getattr(config, 'add_serial', '') or ''  # 扩展码，默认为空
        template_params = message.get_data(self) or []
        
        request_data = {
            "ecName": config.app_secret,     # 企业名称（存储在app_secret中）
            "apId": config.app_id,           # 用户名/账号
            "templateId": message.get_template(self),  # 模板ID
            "mobiles": to.get_number(),      # 手机号码
            "params": json.dumps(template_params, ensure_ascii=False),  # 模板参数
            "sign": config.sign,             # 签名编码
            "addSerial": add_serial          # 扩展码
        }
        
        # 生成MAC签名 (模板短信的签名顺序)
        mac_string = (
            request_data["ecName"] +
            request_data["apId"] +
            config.app_key +
            request_data["templateId"] +
            request_data["mobiles"] +
            request_data["params"] +
            request_data["sign"] +
            request_data["addSerial"]
        )
        request_data["mac"] = hashlib.md5(mac_string.encode('utf-8')).hexdigest().lower()
        
        return self._make_request(request_data, config, is_template=True)

    def _make_request(self, request_data: Dict[str, Any], config: GatewayConfig, is_template: bool = False) -> Dict[str, Any]:
        """发送HTTP请求
        
        Args:
            request_data: 请求数据
            config: 网关配置
            is_template: 是否为模板短信
            
        Returns:
            网关原始响应
        """
        try:
            # 选择端点
            if is_template:
                url = config.endpoint or self.template_endpoint
            else:
                url = config.endpoint or self.default_endpoint
            
            # 将请求数据转换为JSON并进行Base64编码
            json_data = json.dumps(request_data, ensure_ascii=False)
            encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
            
            # 设置请求头
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "senweaver-sms/1.0"
            }
            
            # 发送请求
            response = requests.post(
                url,
                data=encoded_data,
                headers=headers,
                timeout=config.timeout,
                verify=config.ssl_verify
            )
            
            # 检查HTTP状态码
            if response.status_code != 200:
                raise GatewayErrorException(
                    f"HTTP请求失败: {response.status_code}",
                    response.status_code
                )
            
            # 解析响应
            try:
                result = response.json()
            except json.JSONDecodeError:
                raise GatewayErrorException(
                    f"响应格式错误: {response.text}",
                    "INVALID_RESPONSE"
                )
            
            # 检查业务状态码
            if result.get("rspcod") != "success":
                error_code = result.get("rspcod", "UNKNOWN_ERROR")
                error_msg = f"短信发送失败: {error_code}"
                raise GatewayErrorException(error_msg, error_code)
            
            return result
            
        except requests.exceptions.Timeout:
            raise GatewayErrorException("请求超时", "TIMEOUT")
        except requests.exceptions.ConnectionError:
            raise GatewayErrorException("连接错误", "CONNECTION_ERROR")
        except requests.exceptions.RequestException as e:
            raise GatewayErrorException(f"请求异常: {str(e)}", "REQUEST_ERROR")

    def _extract_message_id(self, response: Dict[str, Any]) -> Optional[str]:
        """从响应中提取消息ID
        
        Args:
            response: 网关响应
            
        Returns:
            消息ID，如果没有则返回None
        """
        # 移动mas返回的消息批次号
        return response.get("msgGroup")

    def _get_gateway_name(self) -> str:
        """获取网关名称
        
        Returns:
            网关名称
        """
        return "mas"