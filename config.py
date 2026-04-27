"""
LLM-GAME-Arena 配置文件
从 .env 文件读取配置
"""
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# API配置
API_ENDPOINT = os.getenv('API_ENDPOINT', 'https://api.whatai.cc/v1/chat/completions')
API_KEY = os.getenv('API_KEY', '')

# 超时和重试设置
TIMEOUT_SECONDS = int(os.getenv('TIMEOUT_SECONDS', '30'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# 检查API Key是否配置
if not API_KEY:
    print("警告: API_KEY 未配置，请在 .env 文件中设置")
    print("可以复制 .env.example 为 .env 并填入你的API密钥")