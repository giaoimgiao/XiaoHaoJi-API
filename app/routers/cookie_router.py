"""
Cookie管理路由
"""
from fastapi import APIRouter, Depends, HTTPException

from ..models import (
    CookieSet, CookieGet, CookieResponse,
    ApiResponse, User
)
from ..auth import get_current_active_user
from ..session_manager import session_manager

router = APIRouter(prefix="/cookie", tags=["Cookie管理"])


@router.post("/set", response_model=ApiResponse, summary="设置Cookie")
async def set_cookie(
    cookie_data: CookieSet,
    current_user: User = Depends(get_current_active_user)
):
    """
    设置Cookie到指定会话
    
    **示例:**
    ```json
    {
        "session_id": "my-session",
        "url": "https://example.com",
        "cookies": {
            "session": "abc123",
            "token": "xyz789"
        }
    }
    ```
    """
    session = session_manager.get_session(
        current_user.username, 
        cookie_data.session_id, 
        auto_create=True
    )
    
    session.set_cookies(cookie_data.url, cookie_data.cookies)
    
    return ApiResponse(
        success=True,
        message=f"已设置 {len(cookie_data.cookies)} 个Cookie",
        data={"session_id": cookie_data.session_id}
    )


@router.post("/get", response_model=CookieResponse, summary="获取Cookie")
async def get_cookie(
    cookie_data: CookieGet,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取会话中的Cookie
    
    - **session_id**: 会话ID
    - **url**: 指定URL(可选，不填返回全部)
    
    **示例:**
    ```json
    {
        "session_id": "my-session",
        "url": "https://example.com"
    }
    ```
    """
    session = session_manager.get_session(
        current_user.username, 
        cookie_data.session_id, 
        auto_create=False
    )
    
    if not session:
        raise HTTPException(status_code=404, detail=f"会话 {cookie_data.session_id} 不存在")
    
    cookies = session.get_cookies(cookie_data.url)
    
    return CookieResponse(
        session_id=cookie_data.session_id,
        cookies=cookies
    )


@router.get("/get/{session_id}", response_model=CookieResponse, summary="获取Cookie(简化)")
async def get_cookie_simple(
    session_id: str,
    url: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    简化的获取Cookie接口
    
    - **session_id**: 会话ID (路径参数)
    - **url**: 指定URL (查询参数，可选)
    """
    session = session_manager.get_session(
        current_user.username, 
        session_id, 
        auto_create=False
    )
    
    if not session:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
    
    cookies = session.get_cookies(url)
    
    return CookieResponse(session_id=session_id, cookies=cookies)


@router.delete("/clear/{session_id}", response_model=ApiResponse, summary="清除Cookie")
async def clear_cookie(
    session_id: str,
    url: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    清除会话中的Cookie
    
    - **session_id**: 会话ID
    - **url**: 指定URL(可选，不填清除全部)
    """
    session = session_manager.get_session(
        current_user.username, 
        session_id, 
        auto_create=False
    )
    
    if not session:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
    
    session.clear_cookies(url)
    
    return ApiResponse(
        success=True,
        message="Cookie已清除",
        data={"session_id": session_id}
    )


@router.get("/all/{session_id}", response_model=ApiResponse, summary="获取所有Cookie(按域名分组)")
async def get_all_cookies(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取会话中所有Cookie，按域名分组
    """
    session = session_manager.get_session(
        current_user.username, 
        session_id, 
        auto_create=False
    )
    
    if not session:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
    
    cookies_by_domain = session.get_cookies_by_domain()
    
    return ApiResponse(
        success=True,
        message=f"共 {sum(len(c) for c in cookies_by_domain.values())} 个Cookie",
        data=cookies_by_domain
    )
