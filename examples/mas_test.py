#!/usr/bin/env python3
"""
SenWeaver SMS 移动MAS Test Example
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
    """测试移动MAS短信发送功能 (使用新的Builder API)"""
    # 获取环境变量中的配置
    ap_id = os.getenv('MAS_AP_ID')  # 用户名/账号
    secret_key = os.getenv('MAS_SECRET_KEY')  # 用户密码
    ec_name = os.getenv('MAS_EC_NAME')  # 企业名称
    sign = os.getenv('MAS_SIGN')  # 签名编码
    add_serial = os.getenv('MAS_ADD_SERIAL', '')  # 扩展码，默认为空
    endpoint_url = os.getenv('MAS_ENDPOINT')  # 可选的endpoint
    template_id = os.getenv('MAS_TEMPLATE_ID', 'YOUR_TEMPLATE_ID')  # 请替换或在env中设置
    test_phone = os.getenv('TEST_PHONE_NUMBER')

    if not all([ap_id, secret_key, ec_name, sign]):
        print("错误: 请在 .env 文件中设置所有必需的移动MAS配置")
        print("必需的环境变量: MAS_AP_ID, MAS_SECRET_KEY, MAS_EC_NAME, MAS_SIGN")
        return

    if not test_phone:
        test_phone = input("请输入接收测试短信的手机号: ")
        if not test_phone:
            print("未输入手机号，测试中止。")
            return

    print("使用配置:")
    print(f"  AP_ID: {ap_id[:5]}...{ap_id[-5:]}")
    print(f"  SECRET_KEY: {'*' * len(secret_key)}")
    print(f"  EC_NAME: {ec_name}")
    print(f"  SIGN: {sign}")
    if add_serial:
        print(f"  ADD_SERIAL: {add_serial}")
    if endpoint_url:
        print(f"  ENDPOINT: {endpoint_url}")
    print(f"  TEMPLATE_ID: {template_id}")
    print(f"  测试手机号: {test_phone}")
    print("-" * 20)

    try:
        # 使用构建器创建SMS请求对象
        sms_builder = SMSBuilder.builder() \
            .mas(
                ap_id=ap_id,
                secret_key=secret_key,
                ec_name=ec_name,
                sign=sign,
                add_serial=add_serial,
                endpoint=endpoint_url  # 如果env中设置了则使用
            ) \
            .timeout(10.0) \
            .debug(True)
            
        sms_request = sms_builder.build()
        
        # 测试普通短信发送
        # print(f"\n正在向 {test_phone} 发送普通短信...")
        
        # response = sms_request.send(
        #      to=test_phone, 
        #      content="【短信测试】您的验证码是123456，5分钟内有效。"
        #  )
        
        # print("\n普通短信发送成功!")
        # print(f"网关: {response.gateway}")
        # print(f"状态: {response.status.name}")
        # print(f"消息ID: {response.message_id}")
        # print(f"原始响应: {response.raw_response}")
        
        # 如果设置了模板ID，测试模板短信发送
        if template_id and template_id != 'YOUR_TEMPLATE_ID':
            print(f"\n正在向 {test_phone} 发送模板短信 (Template: {template_id})...")
            
            response = sms_request.send(
                to=test_phone, 
                template=template_id,
                data=['654321']  # 替换为您的模板需要的参数
            )
            
            print("\n模板短信发送成功!")
            print(f"网关: {response.gateway}")
            print(f"状态: {response.status.name}")
            print(f"消息ID: {response.message_id}")
            print(f"原始响应: {response.raw_response}")
        else:
            print("\n跳过模板短信测试 (未设置有效的模板ID)")
        
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