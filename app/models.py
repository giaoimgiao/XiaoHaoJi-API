"""
数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from enum import Enum


# ==================== 认证相关 ====================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class User(BaseModel):
    username: str
    disabled: bool = False


# ==================== HTTP请求相关 ====================

class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HttpRequest(BaseModel):
    """HTTP请求模型"""
    url: str = Field(..., description="请求URL")
    method: HttpMethod = Field(default=HttpMethod.GET, description="请求方法")
    headers: Optional[Dict[str, str]] = Field(default=None, description="请求头")
    params: Optional[Dict[str, str]] = Field(default=None, description="URL参数")
    data: Optional[str] = Field(default=None, description="请求体(表单或原始数据)")
    json_data: Optional[Dict[str, Any]] = Field(default=None, description="JSON请求体")
    cookies: Optional[Dict[str, str]] = Field(default=None, description="Cookie")
    timeout: Optional[int] = Field(default=30, description="超时时间(秒)")
    follow_redirects: bool = Field(default=True, description="是否跟随重定向")
    verify_ssl: bool = Field(default=False, description="是否验证SSL证书")
    proxy: Optional[str] = Field(default=None, description="代理地址")
    
    # 会话相关
    session_id: Optional[str] = Field(default=None, description="会话ID(用于Cookie持久化)")
    save_cookies: bool = Field(default=True, description="是否保存响应Cookie到会话")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://httpbin.org/get",
                "method": "GET",
                "headers": {"User-Agent": "MyApp/1.0"},
                "session_id": "my-session-1"
            }
        }


class HttpResponse(BaseModel):
    """HTTP响应模型"""
    status_code: int = Field(..., description="状态码")
    headers: Dict[str, str] = Field(..., description="响应头")
    cookies: Dict[str, str] = Field(..., description="响应Cookie")
    text: str = Field(..., description="响应文本")
    json_data: Optional[Any] = Field(default=None, description="JSON响应(如果可解析)")
    elapsed_ms: int = Field(..., description="请求耗时(毫秒)")
    final_url: str = Field(..., description="最终URL(重定向后)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "headers": {"Content-Type": "application/json"},
                "cookies": {"session": "abc123"},
                "text": "{\"success\": true}",
                "json_data": {"success": True},
                "elapsed_ms": 150,
                "final_url": "https://httpbin.org/get"
            }
        }


# ==================== Cookie管理相关 ====================

class CookieSet(BaseModel):
    """设置Cookie"""
    session_id: str = Field(..., description="会话ID")
    url: str = Field(..., description="Cookie所属URL/域名")
    cookies: Dict[str, str] = Field(..., description="Cookie键值对")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "my-session-1",
                "url": "https://example.com",
                "cookies": {"session": "abc123", "token": "xyz789"}
            }
        }


class CookieGet(BaseModel):
    """获取Cookie"""
    session_id: str = Field(..., description="会话ID")
    url: Optional[str] = Field(default=None, description="指定URL(不填则获取全部)")


class CookieResponse(BaseModel):
    """Cookie响应"""
    session_id: str
    cookies: Dict[str, str]


# ==================== 会话管理相关 ====================

class Session(BaseModel):
    """会话信息"""
    session_id: str = Field(..., description="会话ID")
    created_at: str = Field(..., description="创建时间")
    last_used: str = Field(..., description="最后使用时间")
    cookie_count: int = Field(..., description="Cookie数量")
    cookies: Optional[Dict[str, Dict[str, str]]] = Field(default=None, description="Cookie详情(按域名分组)")


class SessionCreate(BaseModel):
    """创建会话"""
    session_id: Optional[str] = Field(default=None, description="会话ID(不填则自动生成)")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "my-custom-session"
            }
        }


class SessionList(BaseModel):
    """会话列表"""
    total: int
    sessions: List[Session]


# ==================== 批量请求 ====================

class BatchRequest(BaseModel):
    """批量请求"""
    requests: List[HttpRequest] = Field(..., description="请求列表")
    parallel: bool = Field(default=False, description="是否并行执行")

    class Config:
        json_schema_extra = {
            "example": {
                "requests": [
                    {"url": "https://httpbin.org/get", "method": "GET"},
                    {"url": "https://httpbin.org/post", "method": "POST", "data": "test=1"}
                ],
                "parallel": True
            }
        }


class BatchResponse(BaseModel):
    """批量响应"""
    results: List[HttpResponse]
    total_elapsed_ms: int


# ==================== 通用响应 ====================

class ApiResponse(BaseModel):
    """通用API响应"""
    success: bool
    message: str
    data: Optional[Any] = None
