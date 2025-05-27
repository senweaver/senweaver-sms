"""Base exceptions for SenWeaver SMS."""
from typing import Any, Dict, Optional


class Exception(Exception):
    """Base exception for SenWeaver SMS.

    All exceptions in the SenWeaver SMS package inherit from this class.
    This allows catching all SenWeaver SMS related exceptions using this base class.
    """

    def __init__(self, message: str) -> None:
        """Initialize a new instance.

        Args:
            message: The exception message.
        """
        super().__init__(message)

class GatewayErrorException(Exception):
    """
    网关错误异常
    
    当短信网关返回错误或请求失败时抛出
    """
    
    def __init__(self, message: str, code: Any = None, exception: Optional[Exception] = None, data: Optional[Dict[str, Any]] = None):
        """
        初始化
        
        Args:
            message: 错误消息
            code: 错误代码
            exception: 原始异常
            data: 附加数据
        """
        self.message = message
        self.code = code
        self.exception = exception
        self.data = data or {}
        
        super().__init__(message)
    
    def __str__(self) -> str:
        """
        字符串表示
        
        Returns:
            异常的字符串表示
        """
        if self.code:
            return f"{self.message} (代码: {self.code})"
        return self.message
    

class InvalidArgumentException(Exception):
    """
    无效参数异常
    
    当提供的参数无效时抛出
    """
    
    def __init__(self, message: str):
        """
        初始化
        
        Args:
            message: 错误消息
        """
        self.message = message
        
        super().__init__(message)

class NoGatewayAvailableException(Exception):
    """
    无可用网关异常
    
    当所有配置的网关都无法发送短信时抛出
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        初始化
        
        Args:
            message: 错误消息
            details: 详细错误信息，通常包含每个网关的具体错误
        """
        self.message = message
        self.details = details or {}
        
        super().__init__(message)
    
    def __str__(self) -> str:
        """
        字符串表示
        
        Returns:
            异常的字符串表示
        """
        if self.details and "errors" in self.details:
            errors = ", ".join([f"{k}: {v}" for k, v in self.details["errors"].items()])
            return f"{self.message} - {errors}"
        return self.message

    def get_results(self) -> Dict[str, Any]:
        """
        Get all results from gateway attempts.

        Returns:
            Dict[str, Any]: Results from all gateway attempts
        """
        return self.results

    def get_exceptions(self) -> Dict[str, Exception]:
        """
        Get all exceptions from gateway attempts.

        Returns:
            Dict[str, Exception]: Exceptions from all gateway attempts
        """
        return {
            gateway: result.get('exception')
            for gateway, result in self.results.items()
            if result.get('status') == 'failure' and result.get('exception')
        }

    def get_exception(self, gateway: str) -> Exception:
        """
        Get the exception for a specific gateway.

        Args:
            gateway (str): The gateway name

        Returns:
            Exception: The exception for the gateway
        """
        return self.get_exceptions().get(gateway)

    def get_last_exception(self) -> Exception:
        """
        Get the last exception.

        Returns:
            Exception: The last exception
        """
        exceptions = self.get_exceptions()
        if exceptions:
            return list(exceptions.values())[-1]
        return None

class NoGatewaySelectedException(Exception):
    """
    未选择网关异常
    
    当没有指定任何网关时抛出
    """
    
    def __init__(self, message: str):
        """
        初始化
        
        Args:
            message: 错误消息
        """
        self.message = message
        
        super().__init__(message)