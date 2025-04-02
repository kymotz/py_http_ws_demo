import os
from typing import Optional
from dotenv import load_dotenv

import logging

log = logging.Logger.init_logger("agent")

class Settings:
    def __init__(self):
        # 获取环境类型
        env = os.getenv("APP_ENV", "dev")
        print(f"当前环境: {env}")
        # 加载对应的env文件
        env_file = f".env.{env}" if env != "dev" else ".env.dev"
        load_dotenv(env_file)
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.debug: bool = os.getenv("DEBUG", "true").lower() == "true"
        self.api_host: str = os.getenv("API_HOST", "http://localhost")
        self.api_port: int = int(os.getenv("API_PORT", "8000"))

def get_settings() -> Settings:
    return Settings()


if __name__ == "__main__":
    settings = get_settings()
    print(f'{settings.__dict__}')
    log.info(f"当前环境: {settings.app_env}")
    