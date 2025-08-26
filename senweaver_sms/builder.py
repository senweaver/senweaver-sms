"""
短信请求构建器 - 便于构建和配置短信服务
"""
from typing import Dict, Any, List, Union, Callable, Optional

from .config import SMSConfig, GatewayConfig
from .request import SMSRequest


class SMSBuilder:
    """
    短信请求构建器
    支持链式调用和动态配置
    """
    
    def __init__(self):
        """
        初始化
        """
        self._gateway_configs: Dict[str, GatewayConfig] = {}
        self._default_gateway = None
        self._strategy = "order"
        self._timeout = 5.0
        self._debug = False
    
    @classmethod
    def builder(cls) -> 'SMSBuilder':
        """
        创建构建器实例
        
        Returns:
            构建器实例
        """
        return cls()
    
    def gateway(self, 
                name: str, 
                app_id: Optional[str] = None, 
                app_key: Optional[str] = None, 
                app_secret: Optional[str] = None,
                sign: Optional[str] = None, 
                region: Optional[str] = None, 
                version: Optional[str] = None,
                ssl_verify: bool = True,
                # 百度云
                invoke_id: Optional[str] = None,
                signature_id: Optional[str] = None,
                # 华为云
                channel: Optional[str] = None,
                endpoint: Optional[str] = None,
                callback_url: Optional[str] = None,
                # UCloud
                project_id: Optional[str] = None,
                # 其他所有配置
                **other_options
               ) -> 'SMSBuilder':
        """
        添加或更新网关配置
        
        Args:
            name: 网关名称 (例如: "aliyun", "qcloud")
            app_id: 应用ID/账号/用户名/AccessKeyId/PublicKey等
            app_key: 应用密钥/密码/token/AccessKeySecret/PrivateKey等
            app_secret: 应用密钥2(如果需要)
            sign: 短信签名(SignName/SigContent等)
            region: 区域(如阿里云区域: cn-hangzhou)
            version: API版本(如腾讯云: 2021-01-11)
            ssl_verify: 是否验证SSL证书 (默认 True)
            invoke_id: 百度云 - 调用ID
            signature_id: 百度云 - 签名ID (可选)
            channel: 华为云 - 短信通道号 (sender)
            endpoint: 华为云 - API接入地址 (可选, 默认中国区)
            callback_url: 华为云 - 状态回调地址 (可选)
            project_id: UCloud - 项目ID (可选)
            **other_options: 其他可能需要的配置 (不推荐, 优先使用明确参数)
            
        Returns:
            构建器实例
        """
        # 使用 existing config or create new one
        existing_config = self._gateway_configs.get(name, GatewayConfig())
        
        # Update fields if provided
        if app_id is not None: existing_config.app_id = app_id
        if app_key is not None: existing_config.app_key = app_key
        if app_secret is not None: existing_config.app_secret = app_secret
        if sign is not None: existing_config.sign = sign
        if region is not None: existing_config.region = region
        if version is not None: existing_config.version = version
        existing_config.ssl_verify = ssl_verify # Always update ssl_verify
        if invoke_id is not None: existing_config.invoke_id = invoke_id
        if signature_id is not None: existing_config.signature_id = signature_id
        if channel is not None: existing_config.channel = channel
        if endpoint is not None: existing_config.endpoint = endpoint
        if callback_url is not None: existing_config.callback_url = callback_url
        if project_id is not None: existing_config.project_id = project_id
        
        # Set timeout from builder's current setting
        existing_config.timeout = self._timeout
        
        # Add any other options (less preferred)
        if other_options:
             # Update existing config with other options
             config_dict = existing_config.to_dict()
             config_dict.update(other_options)
             # Recreate GatewayConfig to handle potential new fields not directly supported
             # Note: This might overwrite explicit fields if keys clash
             try:
                 existing_config = GatewayConfig(**config_dict)
             except TypeError as e:
                 print(f"Warning: Failed to update GatewayConfig with other_options for {name}: {e}")

        self._gateway_configs[name] = existing_config
        return self
    
    # --- Specific Gateway Helper Methods --- 
    
    def aliyun(self, access_key_id: str, access_key_secret: str, sign_name: str, region: Optional[str] = None) -> 'SMSBuilder':
        return self.gateway(name="aliyun", app_id=access_key_id, app_key=access_key_secret, sign=sign_name, region=region)
    
    def baidu(self, access_key: str, secret_key: str, invoke_id: str, signature_id: Optional[str] = None) -> 'SMSBuilder':
        return self.gateway(name="baidu", app_id=access_key, app_key=secret_key, invoke_id=invoke_id, signature_id=signature_id)
        
    def ctyun(self, access_key: str, secret_key: str, sign: str) -> 'SMSBuilder':
        return self.gateway(name="ctyun", app_id=access_key, app_key=secret_key, sign=sign)

    def huawei(self, app_key: str, app_secret: str, channel: str, sign: Optional[str] = None, 
                 endpoint: Optional[str] = None, callback_url: Optional[str] = None) -> 'SMSBuilder':
        return self.gateway(name="huawei", app_id=app_key, app_key=app_secret, 
                            channel=channel, sign=sign, 
                            endpoint=endpoint, callback_url=callback_url)
                            
    def huyi(self, account: str, password: str) -> 'SMSBuilder':
        return self.gateway(name="huyi", app_id=account, app_key=password)
    
    def juhe(self, key: str) -> 'SMSBuilder':
        return self.gateway(name="juhe", app_id="", app_key=key)
        
    def qcloud(self, sdk_app_id: str, secret_id: str, secret_key: str, sign_name: str, 
                 version: Optional[str] = None, region: Optional[str] = None) -> 'SMSBuilder':
        return self.gateway(name="qcloud", app_id=sdk_app_id, app_key=secret_id, app_secret=secret_key, 
                            sign=sign_name, version=version, region=region)
                            
    def qiniu(self, access_key: str, secret_key: str) -> 'SMSBuilder':
        return self.gateway(name="qiniu", app_id=access_key, app_key=secret_key)

    def smsbao(self, username: str, password: str, sign: Optional[str] = None) -> 'SMSBuilder':
        return self.gateway(name="smsbao", app_id=username, app_key=password, sign=sign)
        
    def ucloud(self, public_key: str, private_key: str, sig_content: str, project_id: Optional[str] = None) -> 'SMSBuilder':
        return self.gateway(name="ucloud", app_id=public_key, app_key=private_key, sign=sig_content, project_id=project_id)
        
    def yunpian(self, api_key: str, sign: Optional[str] = None) -> 'SMSBuilder':
        return self.gateway(name="yunpian", app_id="", app_key=api_key, sign=sign)
        
    def mas(self, ap_id: str, secret_key: str, ec_name: str, sign: str, add_serial: str = "", endpoint: str = "http://112.35.1.155:1992/sms/norsubmit") -> 'SMSBuilder':
        """
        配置中国移动MAS短信网关
        
        Args:
            ap_id: 应用ID
            secret_key: 密钥
            ec_name: 企业代码
            sign: 签名
            add_serial: 扩展码（可选）
            endpoint: 接口地址
            
        Returns:
            构建器实例
        """
        return self.gateway(name="mas", app_id=ap_id, app_key=secret_key, app_secret=ec_name, sign=sign, 
                           add_serial=add_serial, endpoint=endpoint)

    # --- General Configuration Methods --- 

    def default_gateway(self, name: str) -> 'SMSBuilder':
        """
        设置默认网关
        
        Args:
            name: 网关名称
            
        Returns:
            构建器实例
        """
        self._default_gateway = name
        return self
    
    def strategy(self, strategy: str) -> 'SMSBuilder':
        """
        设置策略
        
        Args:
            strategy: 策略名称
            
        Returns:
            构建器实例
        """
        self._strategy = strategy
        return self
    
    def timeout(self, timeout: float) -> 'SMSBuilder':
        """
        设置全局超时时间 (会覆盖已添加网关的超时设置)
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            构建器实例
        """
        self._timeout = timeout
        # 更新已存在网关的超时设置
        for config in self._gateway_configs.values():
            config.timeout = timeout
        return self
    
    def debug(self, debug: bool = True) -> 'SMSBuilder':
        """
        设置调试模式
        
        Args:
            debug: 是否开启调试模式
            
        Returns:
            构建器实例
        """
        self._debug = debug
        return self
    
    def build(self) -> SMSRequest:
        """
        构建短信请求对象
        
        Returns:
            短信请求对象
        """
        # 至少需要一个网关
        if not self._gateway_configs:
            raise ValueError("至少需要配置一个网关")
        
        # 创建配置
        config = SMSConfig(
            gateways=self._gateway_configs,
            default_gateway=self._default_gateway,
            default_strategy=self._strategy,
            debug=self._debug
        )
        
        # 创建请求对象
        return SMSRequest(config)