"""
XiaoHaoJi API - 主入口
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings
from .routers import auth_router, http_router, cookie_router, session_router

# 创建限流器
limiter = Limiter(key_func=get_remote_address)

# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## XiaoHaoJi HTTP代理API

提供HTTP请求代理、Cookie管理、会话池等功能。

### 功能特性

- **HTTP请求代理**: 支持GET/POST等方法，自定义Headers，代理设置
- **Cookie管理**: 自动保存和发送Cookie，支持按域名管理
- **会话池**: 多账号Cookie隔离，每个会话独立存储
- **请求限流**: 防止滥用，保护服务稳定性
- **API认证**: JWT Token认证，保护接口安全

### 快速开始

1. 调用 `/auth/login` 获取Token
2. 在请求Header中添加 `Authorization: Bearer <token>`
3. 创建会话 `/session/create`
4. 发送请求 `/http/request`

### 使用示例

```python
import requests

# 登录获取Token
resp = requests.post("http://localhost:8000/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = resp.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 发送HTTP请求
resp = requests.post("http://localhost:8000/http/request", 
    headers=headers,
    json={
        "url": "https://httpbin.org/get",
        "method": "GET",
        "session_id": "my-session"
    }
)
print(resp.json())
```
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 添加限流器
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": f"服务器内部错误: {str(exc)}",
            "data": None
        }
    )


# 注册路由
app.include_router(auth_router)
app.include_router(http_router)
app.include_router(cookie_router)
app.include_router(session_router)


# 根路由
@app.get("/", tags=["首页"])
async def root():
    """API首页"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


# 健康检查
@app.get("/health", tags=["健康检查"])
async def health():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
