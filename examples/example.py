from senweaver_sms import SMSBuilder, PhoneNumber


def basic_usage():
    """基本用法示例"""
    # 使用构建器创建SMS请求对象
    sms = SMSBuilder.builder() \
        .smsbao(username="your_username", password="your_password", sign="SenWeaver") \
        .huyi(account="your_api_id", password="your_api_key") \
        .timeout(10.0) \
        .build()
    
    # 发送简单的短信
    response = sms.send("your_phone", content="您的验证码是1234，5分钟内有效。")
    print(response)
    
    # 使用模板发送短信
    response = sms.send(
        PhoneNumber("your_phone"), 
        template="SMS_123456",
        data={"code": "1234", "product": "SenWeaver"}
    )
    print(response)
    
    # 指定网关发送
    response = sms.send(
        "your_phone", 
        content="您的验证码是1234，5分钟内有效。",
        gateways=["smsbao"]
    )
    print(response)


def advanced_usage():
    """高级用法示例"""
    # 使用链式调用添加网关
    sms = SMSBuilder.builder() \
        .gateway(
            name="smsbao",
            app_id="your_username",
            app_key="your_password",
            sign="您的签名"
        ) \
        .juhe(key="your_app_key") \
        .strategy("random") \
        .debug(True) \
        .build()
    
    # 发送短信
    response = sms.send(
        "your_phone", 
        content="您的验证码是1234，5分钟内有效。"
    )
    print(response)


if __name__ == "__main__":
    print("=== 基本用法示例 ===")
    try:
        basic_usage()
    except Exception as e:
        print(f"基本用法示例异常: {e}")
    
    print("\n=== 高级用法示例 ===")
    try:
        advanced_usage()
    except Exception as e:
        print(f"高级用法示例异常: {e}") 