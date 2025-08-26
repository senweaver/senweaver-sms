"""
短信服务配置类 - 统一配置管理
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union


@dataclass
class GatewayConfig:
    """
    网关配置类
    使用通用字段，适用于所有网关
    """
    # --- 通用身份认证信息 ---
    app_id: Optional[str] = None        # 应用ID/账号/用户名/AccessKeyId/PublicKey等
    app_key: Optional[str] = None       # 应用密钥/密码/token/AccessKeySecret/PrivateKey等
    app_secret: Optional[str] = None    # 应用密钥2(如果需要)
    
    # --- 通用可选配置 ---
    sign: Optional[str] = None          # 短信签名(SignName/SigContent等)
    region: Optional[str] = None        # 区域(如阿里云区域: cn-hangzhou)
    version: Optional[str] = None       # API版本(如腾讯云: 2021-01-11)
    
    # --- 通用高级配置 ---
    timeout: float = 5.0                # 请求超时时间(秒)
    ssl_verify: bool = True             # 是否验证SSL证书
    
    # --- 特定网关配置 ---
    # 百度云 (baidu)
    invoke_id: Optional[str] = None     # 调用ID
    signature_id: Optional[str] = None  # 签名ID (可选)
    
    # 华为云 (huawei)
    channel: Optional[str] = None        # 短信通道号 (sender)
    endpoint: Optional[str] = None       # API接入地址 (可选, 默认中国区)
    callback_url: Optional[str] = None   # 状态回调地址 (可选)
    
    # UCloud (ucloud)
    project_id: Optional[str] = None     # 项目ID (可选)
    
    # 移动mas (mas)
    add_serial: Optional[str] = None     # 扩展码 (可选, 默认为空字符串)
    
    def __post_init__(self):
        """
        初始化后的处理，验证必要的配置
        """
        pass  # 通用配置不做强制验证，由各网关自行验证
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将配置转换为字典 (主要用于调试或序列化)
        
        Returns:
            配置字典
        """
        result = {}
        # Use dataclasses.fields to iterate through fields
        import dataclasses
        for f in dataclasses.fields(self.__class__):
            value = getattr(self, f.name)
            if value is not None:
                result[f.name] = value
        return result


@dataclass
class SMSConfig:
    """
    短信服务主配置类
    """
    gateways: Dict[str, GatewayConfig] = field(default_factory=dict)
    default_gateway: Optional[str] = None      # 默认网关
    default_strategy: str = "order"            # 默认策略
    debug: bool = False                        # 调试模式
    
    def __post_init__(self):
        """
        初始化后的处理
        """
        if not self.gateways:
            raise ValueError("至少需要配置一个网关")
        
        # 如果未指定默认网关，使用第一个网关
        if not self.default_gateway and self.gateways:
            self.default_gateway = next(iter(self.gateways.keys()))
    
    def add_gateway(self, name: str, config: GatewayConfig) -> 'SMSConfig':
        """
        添加网关配置
        
        Args:
            name: 网关名称
            config: 网关配置
            
        Returns:
            更新后的配置对象
        """
        self.gateways[name] = config
        return self
    
    def get_gateway(self, name: str) -> Optional[GatewayConfig]:
        """
        获取网关配置
        
        Args:
            name: 网关名称
            
        Returns:
            网关配置，如果不存在返回None
        """
        return self.gateways.get(name)
    
    def get_default_gateway(self) -> Optional[GatewayConfig]:
        """
        获取默认网关配置
        
        Returns:
            默认网关配置，如果不存在返回None
        """
        if not self.default_gateway:
            return None
        return self.gateways.get(self.default_gateway)
    
    def set_default_gateway(self, name: str) -> 'SMSConfig':
        """
        设置默认网关
        
        Args:
            name: 网关名称
            
        Returns:
            更新后的配置对象
        """
        if name not in self.gateways:
            raise ValueError(f"网关 {name} 不存在")
        self.default_gateway = name
        return self