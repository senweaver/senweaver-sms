# SenWeaver SMS

📲 您的一站式 Python 短信发送解决方案

> 告别繁琐的多平台适配！本库聚合了众多短信服务商，通过一致的调用方式、灵活的配置选项和内置的轮询策略，让您轻松实现高效、可靠的短信发送，并获得统一的响应结果用于监控。

[![PyPI version](https://badge.fury.io/py/senweaver-sms.svg)](https://badge.fury.io/py/senweaver-sms)

## 特点

1. 支持目前市面多家服务商
2. 一套写法兼容所有平台
3. 提供流畅的 Builder API，配置简单灵活
4. 内置多种服务商轮询策略、支持自定义轮询策略
5. 统一的返回值格式 (`SMSResponse`)，便于日志与监控
6. 自动根据策略选择可用的服务商
7. 类型提示友好，代码健壮性高

## 平台支持

* 阿里云 (Aliyun)
* 腾讯云 (Qcloud)
* 百度智能云 (Baidu)
* 华为云 (Huawei)
* 天翼云 (Ctyun)
* UCloud
* 七牛云 (Qiniu)
* 云片 (Yunpian)
* 互亿无线 (Huyi)
* 聚合数据 (Juhe)
* 短信宝 (Smsbao)
* 持续添加中...

## 环境需求

* Python >= 3.8

## 安装

```bash
pip install senweaver-sms
```

## 使用 (推荐方式: SMSBuilder)

我们推荐使用 `SMSBuilder` 来构建和发送短信请求，它提供了链式调用和类型安全的配置方式。

```python
from senweaver_sms import SMSBuilder, PhoneNumber
from senweaver_sms.exception import GatewayErrorException, NoGatewayAvailableException

# 使用构建器配置网关
sms_request = SMSBuilder.builder() \
    .aliyun( # 添加阿里云网关
        access_key_id="YOUR_ALIYUN_ACCESS_KEY_ID",
        access_key_secret="YOUR_ALIYUN_ACCESS_KEY_SECRET",
        sign_name="你的签名"
    ) \
    .qcloud( # 添加腾讯云网关
        sdk_app_id="YOUR_TENCENT_SDK_APP_ID",
        secret_id="YOUR_TENCENT_SECRET_ID",
        secret_key="YOUR_TENCENT_SECRET_KEY",
        sign_name="你的签名"
    ) \
    .huawei( # 添加华为云网关
        app_key="YOUR_HUAWEI_APP_KEY", # 注意：华为云的app_key是控制台的APP Key
        app_secret="YOUR_HUAWEI_APP_SECRET", # 注意：华为云的app_secret是控制台的APP Secret
        channel="YOUR_HUAWEI_CHANNEL", # 短信通道号
        sign="你的签名" # 可选，不填则尝试用 channel
    ) \
    .yunpian( # 添加云片网关
        api_key="YOUR_YUNPIAN_API_KEY",
        sign="你的签名" # 可选
    ) \
    .timeout(10.0) # 设置全局请求超时时间 (秒)
    .strategy("order") # 设置网关选择策略 ('order', 'random' 或自定义)
    .debug(True) # 开启调试模式 (可选)
    .build() # 构建请求对象

# 发送短信
try:
    phone = "YOUR_PHONE_NUMBER"
    template_id = "YOUR_TEMPLATE_ID" # 不同平台模板ID可能不同
    data = {"code": "123456", "minutes": 5}
    
    print(f"向 {phone} 发送短信...")
    # send 方法参数：接收者手机号, content(可选,文本内容), template(可选,模板ID), data(可选,模板参数), gateways(可选,指定网关列表), strategy(可选,指定策略)
    response = sms_request.send(
        to=phone, 
        template=template_id, 
        data=data
    )
    
    print("\n发送成功!")
    print(f"网关: {response.gateway}")
    print(f"状态: {response.status.name}") # SUCCESS 或 FAILED
    print(f"消息ID: {response.message_id}") # 网关返回的消息标识
    print(f"原始响应: {response.raw_response}")

except (GatewayErrorException, NoGatewayAvailableException) as e:
    print(f"\n发送失败: {e}")
    if isinstance(e, GatewayErrorException):
        print(f"  错误网关: {e.gateway}")
        print(f"  错误代码: {e.code}")
        print(f"  错误详情: {e.data}")
    elif isinstance(e, NoGatewayAvailableException):
        print("  没有可用的网关成功发送短信。尝试详情:")
        if hasattr(e, 'details') and e.details and 'responses' in e.details:
            for failed_resp in e.details['responses']:
                print(f"    - 网关 {failed_resp.gateway} 失败: {failed_resp.error}")

except ValueError as e:
    print(f"\n配置或参数错误: {e}")
    
except Exception as e:
    print(f"\n发生未知错误: {e}")

# 发送国际短信 (使用PhoneNumber对象)
try:
    number = PhoneNumber('YOUR_PHONE_NUMBER', '31') # 31是荷兰的国家码
    print(f"\n向 {number.get_universal_format()} 发送国际短信...")
    response = sms_request.send(
        to=number,
        template=template_id,
        data=data
    )
    print("发送成功!")
    print(f"消息ID: {response.message_id}")
except Exception as e:
    print(f"发送失败: {e}")
    
# 批量发送 (同一内容给多人)
try:
    phones = ["YOUR_PHONE_NUMBER1", "YOUR_PHONE_NUMBER2"]
    print(f"\n向 {len(phones)} 个号码批量发送短信...")
    batch_response = sms_request.batch_send(
        to_list=phones,
        template=template_id,
        data=data
    )
    print(f"批量发送完成: {batch_response.success_count} 成功, {batch_response.failure_count} 失败")
    for resp in batch_response.get_failed_responses():
        print(f"  - {resp.phone_number} 发送失败: {resp.error}")
except Exception as e:
    print(f"批量发送失败: {e}")
```

## 网关配置 (`GatewayConfig`)

使用 `SMSBuilder` 添加网关时，可以通过特定网关的辅助方法（如 `.aliyun()`, `.qcloud()`）或通用的 `.gateway()` 方法进行配置。`GatewayConfig` 对象包含了所有可能的配置项：

* 通用认证: `app_id`, `app_key`, `app_secret`
* 通用选项: `sign`, `region`, `version`
* 通用高级: `timeout`, `ssl_verify`
* 特定网关: `invoke_id` (百度), `signature_id` (百度), `channel` (华为), `endpoint` (华为), `callback_url` (华为), `project_id` (UCloud)

详细的参数映射关系请参考 `senweaver_sms/config.py` 中的 `GatewayConfig` 类文档字符串。

## 短信内容 (`Message`)

发送短信时，可以通过 `content` 参数发送纯文本内容（适用于云片、短信宝等），或通过 `template` 和 `data` 参数使用模板发送（适用于阿里云、腾讯云等）。

```python
# 文本内容发送
sms_request.send(phone, content="【签名】您的验证码是1234")

# 模板发送
sms_request.send(phone, template="TEMPLATE_ID", data={"code": 1234})
```

`data` 参数可以是字典或列表（部分网关如腾讯云、UCloud会按顺序使用列表中的值）。

## 统一响应 (`SMSResponse` / `SMSBatchResponse`)

* **单条发送**: `send` 方法返回一个 `SMSResponse` 对象，包含：
    * `gateway` (str): 实际发送成功的网关名称。
    * `status` (SMSStatus): `SMSStatus.SUCCESS` 或 `SMSStatus.FAILED`。
    * `message_id` (Optional[str]): 网关返回的消息唯一标识 (如果可用)。
    * `raw_response` (Dict[str, Any]): 网关返回的原始响应数据。
    * `error` (Optional[SMSError]): 如果失败，包含错误代码和消息。
    * `fee` (int): 预估的计费条数。
    * `send_time` (datetime): 发送时间。
* **批量发送**: `batch_send` 方法返回一个 `SMSBatchResponse` 对象，包含一个 `SMSResponse` 列表以及成功和失败的统计。

## 异常处理

* `GatewayErrorException`: 特定网关发送失败时抛出，包含错误代码、消息和原始数据。
* `NoGatewayAvailableException`: 所有尝试的网关都发送失败时抛出。
* `NoGatewaySelectedException`: 没有配置任何可用网关时抛出。
* `InvalidArgumentException`: 配置或参数无效时抛出。
* `ValueError`: 配置验证失败时抛出。

## 自定义网关与策略

(这部分可以保持不变或根据需要简化)

...

## 贡献

欢迎提交 Pull Request 或 Issue！

## License

MIT License