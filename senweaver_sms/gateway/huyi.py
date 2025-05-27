import requests
from typing import Dict, Any, Optional

from ..phone_number import PhoneNumber
from ..message import Message
from ..exception.exception import GatewayErrorException
from ..config import GatewayConfig
from .base import BaseGateway

class HuyiGateway(BaseGateway):
    """
    互亿无线网关 (ihuyi.com)
    
    通过互亿无线SMS服务发送短信
    """

    endpoint = "http://106.ihuyi.com/webservice/sms.php?method=Submit"

    def _validate_config(self, config: GatewayConfig) -> None:
        """
        验证配置是否有效
        
        Args:
            config: 网关配置
            
        Raises:
            ValueError: 配置无效时抛出
        """
        if not config.app_id:
            raise ValueError("缺少必要参数: app_id (互亿无线账号)")
        if not config.app_key:
            raise ValueError("缺少必要参数: app_key (互亿无线密码)")

    def _send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """
        使用互亿无线SMS服务发送短信
        
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
            response_text = response.text
            
            # 响应是XML格式，手动解析
            if "<code>2</code>" not in response_text:
                # 在XML中查找错误代码和消息
                code = self._parse_xml(response_text, "code")
                msg = self._parse_xml(response_text, "msg")
                raise GatewayErrorException(
                    msg or "未知错误",
                    code or "UNKNOWN_ERROR",
                    {"response": response_text}
                )
            
            return {
                "code": 2,
                "msg": "发送成功",
                "smsid": self._parse_xml(response_text, "smsid")
            }
        except requests.exceptions.RequestException as e:
            raise GatewayErrorException(str(e), "REQUEST_ERROR", e)
        except Exception as e:
            if isinstance(e, GatewayErrorException):
                raise e
            raise GatewayErrorException(str(e), "UNKNOWN_ERROR", e)

    def _extract_message_id(self, response: Dict[str, Any]) -> Optional[str]:
        """从互亿无线响应中提取消息ID (smsid)"""
        # 成功时 _send 方法已经解析并返回了 smsid
        return response.get("smsid")

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
        # 获取内容
        content = message.get_content(self)
        if not content:
            raise GatewayErrorException("短信内容不能为空", "CONTENT_ERROR")
        
        # 格式化手机号
        phone_number = to.get_number()
        
        return {
            "account": config.app_id,
            "password": config.app_key,
            "mobile": phone_number,
            "content": content,
        }

    def _parse_xml(self, xml_string: str, tag: str) -> str:
        """
        简单的XML解析器，用于从标签中提取值
        
        Args:
            xml_string: 要解析的XML字符串
            tag: 要提取值的标签
            
        Returns:
            标签内的值，如果未找到则返回空字符串
        """
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"
        start_index = xml_string.find(start_tag)
        end_index = xml_string.find(end_tag)
        
        if start_index != -1 and end_index != -1:
            return xml_string[start_index + len(start_tag) : end_index]
        return "" 