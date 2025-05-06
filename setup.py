import os
import re
from setuptools import setup, find_packages

# Read version from __init__.py
with open(os.path.join('senweaver_sms', '__init__.py'), 'r', encoding='utf-8') as f:
    version = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read()).group(1)

# Read README.md for long description
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='senweaver-sms',
    version=version,
    description='您的一站式 Python 短信发送解决方案',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='senweaver',
    url='https://github.com/senweaver/senweaver-sms',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
    keywords='sms, message, yunpian, aliyun, qcloud, tencent, senweaver',
    install_requires=[
        'requests>=2.20.0',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/senweaver/senweaver-sms/issues',
        'Source': 'https://github.com/senweaver/senweaver-sms',
    },
)