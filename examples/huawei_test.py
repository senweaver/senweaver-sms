#!/usr/bin/env python3
"""
SenWeaver SMS Huawei Cloud Test Example
"""

import os
import sys
import dotenv
from pathlib import Path
from senweaver_sms import SMSBuilder
from senweaver_sms.exception import GatewayErrorException, NoGatewayAvailableException

# 加载环境变量
env_path = Path(__file__).parent / '.env'
dotenv.load_dotenv(env_path)

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def main():
    """测试华为云短信发送功能 (使用新的Builder API)"""
    # 获取环境变量中的配置
    app_id = os.getenv('HUAWEI_APP_KEY')
    app_key = os.getenv('HUAWEI_APP_SECRET')
    channel = os.getenv('HUAWEI_CHANNEL') # 使用新的 channel 变量
    sign = os.getenv('HUAWEI_SIGNATURE', channel)  # 默认使用channel作为签名
    endpoint_url = os.getenv('HUAWEI_ENDPOINT') # 可选的endpoint
    template_id = os.getenv('HUAWEI_TEMPLATE_ID', 'YOUR_TEMPLATE_ID') # 请替换或在env中设置
    test_phone = os.getenv('TEST_PHONE_NUMBER')

    if not all([app_id, app_key, channel]):
        print("错误: 请在 .env 文件中设置所有必需的华为云配置")
        print("必需的环境变量: HUAWEI_APP_KEY, HUAWEI_APP_SECRET, HUAWEI_CHANNEL")
        return

    if not test_phone:
        test_phone = input("请输入接收测试短信的手机号: ")
        if not test_phone:
            print("未输入手机号，测试中止。")
            return

    print("使用配置:")
    print(f"  APP_ID: {app_id[:5]}...{app_id[-5:]}")
    print(f"  APP_KEY: {'*' * len(app_key)}")
    print(f"  CHANNEL: {channel}")
    print(f"  SIGN: {sign}")
    if endpoint_url: print(f"  ENDPOINT: {endpoint_url}")
    print(f"  TEMPLATE_ID: {template_id}")
    print(f"  测试手机号: {test_phone}")
    print("-" * 20)

    try:
        # 使用构建器创建SMS请求对象
        sms_builder = SMSBuilder.builder() \
            .huawei(
                app_key=app_id,        # 注意：华为云的app_key对应SDK的app_id
                app_secret=app_key,    # 注意：华为云的app_secret对应SDK的app_key
                channel=channel,
                sign=sign,
                endpoint=endpoint_url # 如果env中设置了则使用
            ) \
            .timeout(10.0) \
            .debug(True)
            
        sms_request = sms_builder.build()
            
        # 发送短信
        print(f"\n正在向 {test_phone} 发送测试短信 (Template: {template_id})...")
        
        response = sms_request.send(
            to=test_phone, 
            template=template_id,
            data={'code': '654321'} # 替换为您的模板需要的参数
        )
        
        print("\n短信发送成功!")
        print(f"网关: {response.gateway}")
        print(f"状态: {response.status.name}")
        print(f"消息ID: {response.message_id}")
        print(f"原始响应: {response.raw_response}")
        
        # 华为云发送接口不直接返回taskId，通常通过回调获取状态
        # 如果需要查询，可能需要单独实现或使用华为云官方SDK

    except (GatewayErrorException, NoGatewayAvailableException) as e:
        print(f"\n短信发送失败: {e}")
        if isinstance(e, GatewayErrorException):
            print(f"  错误代码: {e.code}")
            print(f"  错误详情: {e.data}")
        elif isinstance(e, NoGatewayAvailableException):
            print("  没有可用的网关来发送短信。")
            if hasattr(e, 'details') and e.details and 'responses' in e.details:
                 for failed_resp in e.details['responses']:
                      print(f"    - 网关 {failed_resp.gateway} 失败: {failed_resp.error}")
                      
    except ValueError as e:
         print(f"\n配置错误: {e}")
         
    except Exception as e:
        print(f"\n发生未知错误: {e}")

if __name__ == '__main__':
    main() 