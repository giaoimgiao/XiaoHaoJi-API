"""
配置文件
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "XiaoHaoJi API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API密钥配置
    API_SECRET_KEY: str = "your-secret-key-change-in-production"
    API_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # 管理员配置
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"  # 生产环境请修改
    
    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Redis配置 (可选，用于分布式限流和会话存储)
    REDIS_URL: Optional[str] = None  # "redis://localhost:6379"
    
    # HTTP请求配置
    HTTP_TIMEOUT: int = 30
    HTTP_MAX_REDIRECTS: int = 10
    HTTP_USER_AGENT: str = "XiaoHaoJi-API/1.0"
    
    # 会话池配置
    MAX_SESSIONS_PER_USER: int = 100
    SESSION_EXPIRE_HOURS: int = 24
    
    class Config:
        env_file = ".env"


settings = Settings()
