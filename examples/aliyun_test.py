#!/usr/bin/env python3
"""
SenWeaver SMS Aliyun Test Example
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
    """测试阿里云短信发送功能 (使用新的Builder API)"""
    # 获取环境变量中的配置
    access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID')
    access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
    sign_name = os.getenv('ALIYUN_SIGN_NAME')
    region_id = os.getenv('ALIYUN_REGION_ID', 'cn-hangzhou')
    template_id = os.getenv('ALIYUN_TEMPLATE_ID', 'YOUR_TEMPLATE_ID') # 请替换或在env中设置
    test_phone = os.getenv('TEST_PHONE_NUMBER')

    if not all([access_key_id, access_key_secret, sign_name]):
        print("错误: 请在 .env 文件中设置所有必需的阿里云配置")
        print("必需的环境变量: ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET, ALIYUN_SIGN_NAME")
        return
        
    if not test_phone:
        test_phone = input("请输入接收测试短信的手机号: ")
        if not test_phone:
            print("未输入手机号，测试中止。")
            return
            
    print("使用配置:")
    print(f"  ACCESS_KEY_ID: {access_key_id[:5]}...{access_key_id[-5:]}")
    print(f"  ACCESS_KEY_SECRET: {'*' * len(access_key_secret)}")
    print(f"  SIGN_NAME: {sign_name}")
    print(f"  REGION_ID: {region_id}")
    print(f"  TEMPLATE_ID: {template_id}")
    print(f"  测试手机号: {test_phone}")
    print("-" * 20)
    
    try:
        # 使用构建器创建SMS请求对象
        sms_builder = SMSBuilder.builder() \
            .aliyun(
                access_key_id=access_key_id,
                access_key_secret=access_key_secret,
                sign_name=sign_name,
                region=region_id
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
        # 阿里云SendSms接口通常返回BizId
        biz_id = response.raw_response.get('BizId')
        if biz_id:
            print(f"业务ID (BizId): {biz_id}")
        print(f"原始响应: {response.raw_response}")
        
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