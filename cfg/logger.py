import sys
import os
from loguru import logger
from typing import Dict, Any

class Logger:
    @staticmethod
    def make_filter(name: str):
        def filter(record):
            return record["extra"].get("name") == name
        return filter

    @staticmethod
    def init_logger(
        name: str, 
        log_path: str = "logs", 
        level: str = "INFO",
        rotation: str = "10 MB",
        retention: str = "1 week"
    ):
        # 确保日志目录存在
        if not os.path.exists(log_path):
            os.makedirs(log_path)
            
        # 配置日志格式
        fmt = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

        # 移除默认处理器
        logger.remove()
        
        # 添加控制台处理器
        logger.add(
            sys.stdout,
            format=fmt,
            level=level,
            filter=Logger.make_filter(name)
        )
        
        # 添加文件处理器
        logger.add(
            os.path.join(log_path, f"{name}.log"),
            format=fmt,
            level=level,
            rotation=rotation,
            retention=retention,
            filter=Logger.make_filter(name),
            encoding="utf-8"
        )
        
        return logger.bind(name=name)