"""
Tests for Message class.
"""

import unittest
from senweaver_sms import Message
from unittest.mock import Mock

class MessageTest(unittest.TestCase):
    """Test the Message class."""

    def test_get_content(self):
        """Test getting the content."""
        message = Message(content='Hello')
        self.assertEqual('Hello', message.get_content())

    def test_get_content_callable(self):
        """Test getting the content from a callable."""
        gateway = Mock()
        gateway.get_name.return_value = 'mock'
        message = Message(content=lambda g: f'Hello {g.get_name()}')
        self.assertEqual('Hello mock', message.get_content(gateway))

    def test_get_template(self):
        """Test getting the template."""
        message = Message(template='SMS_001')
        self.assertEqual('SMS_001', message.get_template())

    def test_get_template_callable(self):
        """Test getting the template from a callable."""
        gateway = Mock()
        gateway.get_name.return_value = 'mock'
        message = Message(template=lambda g: f'SMS_{g.get_name()}')
        self.assertEqual('SMS_mock', message.get_template(gateway))

    def test_get_data(self):
        """Test getting the data."""
        message = Message(data={'code': 1234})
        self.assertEqual({'code': 1234}, message.get_data())

    def test_get_data_callable(self):
        """Test getting the data from a callable."""
        gateway = Mock()
        gateway.get_name.return_value = 'mock'
        message = Message(data=lambda g: {'code': 1234, 'gateway': g.get_name()})
        self.assertEqual({'code': 1234, 'gateway': 'mock'}, message.get_data(gateway))

    def test_get_strategy(self):
        """Test getting the strategy."""
        message = Message(strategy='order')
        self.assertEqual('order', message.get_strategy())

    def test_get_gateways(self):
        """Test getting the gateways."""
        message = Message(gateways=['yunpian', 'aliyun'])
        self.assertEqual(['yunpian', 'aliyun'], message.get_gateways())

if __name__ == '__main__':
    unittest.main() 