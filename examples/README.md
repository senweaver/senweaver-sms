# SenWeaver SMS 示例

本目录包含 SenWeaver SMS 的使用示例，帮助您快速上手使用各种短信网关。

## 环境设置

在运行示例前，请先创建一个 `.env` 文件，用于存储您的配置信息。您可以参考以下模板创建自己的 `.env` 文件：

```env
# SenWeaver SMS Configuration

# 通用配置
SMS_TIMEOUT=5.0
SMS_DEFAULT_STRATEGY=order

# 阿里云短信配置
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_SIGN_NAME=your_sign_name
ALIYUN_REGION_ID=cn-hangzhou

# 华为云短信配置
HUAWEI_APP_KEY=your_app_key
HUAWEI_APP_SECRET=your_app_secret
HUAWEI_SENDER=your_sender_id
HUAWEI_SIGNATURE=your_signature

# 腾讯云短信配置
QCLOUD_SECRET_ID=your_secret_id
QCLOUD_SECRET_KEY=your_secret_key
QCLOUD_SDK_APPID=your_sdk_appid
QCLOUD_SIGN=your_sign_name

# 云片短信配置
YUNPIAN_API_KEY=your_api_key
YUNPIAN_SIGNATURE=your_signature

# 百度云短信配置
BAIDU_ACCESS_KEY_ID=your_access_key_id
BAIDU_SECRET_ACCESS_KEY=your_secret_access_key
BAIDU_ENDPOINT=your_endpoint
BAIDU_SIGNATURE=your_signature
BAIDU_INVOKE_ID=your_invoke_id

# 七牛云短信配置
QINIU_ACCESS_KEY=your_access_key
QINIU_SECRET_KEY=your_secret_key
QINIU_SIGNATURE=your_signature

# UCloud短信配置
UCLOUD_PUBLIC_KEY=your_public_key
UCLOUD_PRIVATE_KEY=your_private_key
UCLOUD_PROJECT_ID=your_project_id
UCLOUD_SIGNATURE=your_signature

# 短信宝配置
SMSBAO_USER=your_username
SMSBAO_PASSWORD=your_password
SMSBAO_SIGNATURE=your_signature

# 聚合数据短信配置
JUHE_KEY=your_app_key
JUHE_TPL_ID=your_template_id

# 互亿无线短信配置
HUYI_ACCOUNT=your_account
HUYI_PASSWORD=your_password

# 天翼云短信配置
CTYUN_APP_ID=your_app_id
CTYUN_APP_SECRET=your_app_secret
CTYUN_TEMPLATE_ID=your_template_id
```

请根据您实际使用的短信网关，填写相应的配置信息。

## 依赖安装

运行示例前，请确保已安装所需的依赖：

```bash
pip install python-dotenv
```

## 示例文件

- `basic_usage.py`: 基本用法示例，展示了 SenWeaver SMS 的核心功能
- `aliyun_test.py`: 阿里云短信发送测试示例
- 更多网关的示例后续会添加...

## 运行示例

```bash
# 基本用法示例
python basic_usage.py

# 阿里云测试示例
python aliyun_test.py
```

## 短信网关配置说明

### 阿里云短信网关

阿里云短信网关需要以下配置：

- `access_key_id`: 阿里云账号的 AccessKey ID
- `access_key_secret`: 阿里云账号的 AccessKey Secret
- `sign_name`: 短信签名
- `region_id`: 地域ID，默认为 cn-hangzhou

您可以在阿里云控制台的 [AccessKey 管理页面](https://ram.console.aliyun.com/manage/ak) 获取 AccessKey，在 [短信服务控制台](https://dysms.console.aliyun.com/) 管理短信签名和模板。

### 华为云短信网关

华为云短信网关需要以下配置：

- `app_key`: 华为云账号的 AppKey
- `app_secret`: 华为云账号的 AppSecret
- `sender`: 短信发送通道号
- `signature`: 短信签名

您可以在华为云控制台的 [短信服务](https://console.huaweicloud.com/sms/) 获取相关信息。

### 腾讯云短信网关

腾讯云短信网关需要以下配置：

- `secret_id`: 腾讯云账号的 SecretId
- `secret_key`: 腾讯云账号的 SecretKey
- `sdk_appid`: 应用 SDK AppID
- `sign`: 短信签名

您可以在腾讯云控制台的 [短信服务](https://console.cloud.tencent.com/smsv2) 获取相关信息。

### 其他网关

其他网关的配置说明请参考各自的官方文档。 