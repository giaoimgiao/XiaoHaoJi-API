"""
认证路由
"""
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status

from ..config import settings
from ..models import Token, UserLogin, ApiResponse
from ..auth import authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=Token, summary="用户登录")
async def login(user_login: UserLogin):
    """
    用户登录获取Token
    
    - **username**: 用户名
    - **password**: 密码
    
    返回JWT Token，后续请求需要在Header中携带:
    ```
    Authorization: Bearer <token>
    ```
    """
    user = authenticate_user(user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/info", response_model=ApiResponse, summary="获取当前用户信息")
async def get_info():
    """获取API基本信息(无需认证)"""
    return ApiResponse(
        success=True,
        message="API服务正常",
        data={
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "rate_limit": f"{settings.RATE_LIMIT_PER_MINUTE}/分钟"
        }
    )
