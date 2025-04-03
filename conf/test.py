import os
from typing import Optional
from dotenv import load_dotenv


"""
配置类
单例对象
"""
class Settings:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            env = os.getenv("APP_ENV", "dev")
            print(f"当前环境: {env}")
            env_file = f".env.{env}" if env != "dev" else ".env.dev"
            load_dotenv(env_file)
            cls._instance.app_env = os.getenv("APP_ENV", "development")
            cls._instance.debug = os.getenv("DEBUG", "true").lower() == "true"
            cls._instance.api_host = os.getenv("API_HOST", "http://localhost")
            cls._instance.api_port = int(os.getenv("API_PORT", "8000"))
        return cls._instance

    def __init__(self):
        pass  # 初始化代码已移到 __new__ 中

def get_settings() -> Settings:
    return Settings()