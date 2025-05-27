import requests
from typing import Dict, Any, Optional

from ..phone_number import PhoneNumber
from ..message import Message
from ..exception.exception import GatewayErrorException
from ..config import GatewayConfig
from .base import BaseGateway

class JuheGateway(BaseGateway):
    """
    聚合数据网关
    
    通过聚合数据短信服务发送短信
    """

    endpoint = "http://v.juhe.cn/sms/send"

    def _validate_config(self, config: GatewayConfig) -> None:
        """
        验证配置是否有效
        
        Args:
            config: 网关配置
            
        Raises:
            ValueError: 配置无效时抛出
        """
        if not config.app_key:
            raise ValueError("缺少必要参数: app_key (聚合数据AppKey)")

    def _send(self, to: PhoneNumber, message: Message, config: GatewayConfig) -> Dict[str, Any]:
        """
        使用聚合数据短信服务发送短信
        
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
            # 使用requests发送请求
            response = requests.get(
                self.endpoint,
                params=params,
                timeout=config.timeout,
                verify=config.ssl_verify
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("error_code") != 0:
                raise GatewayErrorException(
                    result.get("reason", "未知错误"),
                    result.get("error_code", "UNKNOWN_ERROR"),
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
        """从聚合数据响应中提取消息ID (sid)"""
        result_data = response.get("result")
        if isinstance(result_data, dict):
            return result_data.get("sid")
        return None

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
        
        # 格式化手机号
        phone_number = to.get_number()
        
        # 获取模板参数
        template_params = message.get_data(self) or {}
        
        # 格式化参数
        tpl_value = ""
        if template_params:
            if isinstance(template_params, dict):
                # 将字典转换为聚合格式 (#key#=value&#key2#=value2)
                tpl_value = requests.utils.urlencode(
                    {f"#{k}#": v for k, v in template_params.items()}
                )
            elif isinstance(template_params, list):
                # 假设列表对应 #code#, #code2# 等
                tpl_dict = {}
                for i, v in enumerate(template_params):
                    tpl_dict[f"#code{i+1 if i > 0 else ''}#"] = v
                tpl_value = requests.utils.urlencode(tpl_dict)
        
        return {
            "mobile": phone_number,
            "tpl_id": template_id,
            "tpl_value": tpl_value,
            "key": config.app_key,
        } 