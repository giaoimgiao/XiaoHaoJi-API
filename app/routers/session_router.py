"""
会话管理路由
"""
from fastapi import APIRouter, Depends, HTTPException

from ..models import (
    Session, SessionCreate, SessionList,
    ApiResponse, User
)
from ..auth import get_current_active_user
from ..session_manager import session_manager

router = APIRouter(prefix="/session", tags=["会话管理"])


@router.post("/create", response_model=ApiResponse, summary="创建会话")
async def create_session(
    session_data: SessionCreate = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新的Cookie会话
    
    - **session_id**: 自定义会话ID(可选，不填自动生成)
    
    每个会话拥有独立的Cookie存储，适用于多账号场景。
    
    **示例:**
    ```json
    {
        "session_id": "account-1"
    }
    ```
    """
    try:
        session_id = session_data.session_id if session_data else None
        new_session_id = session_manager.create_session(current_user.username, session_id)
        
        return ApiResponse(
            success=True,
            message="会话创建成功",
            data={"session_id": new_session_id}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list", response_model=SessionList, summary="列出所有会话")
async def list_sessions(
    current_user: User = Depends(get_current_active_user)
):
    """
    列出当前用户的所有会话
    """
    sessions = session_manager.list_sessions(current_user.username)
    
    return SessionList(
        total=len(sessions),
        sessions=[Session(**s) for s in sessions]
    )


@router.get("/get/{session_id}", response_model=Session, summary="获取会话详情")
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定会话的详细信息
    """
    session = session_manager.get_session(
        current_user.username, 
        session_id, 
        auto_create=False
    )
    
    if not session:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
    
    return Session(**session.to_dict())


@router.delete("/delete/{session_id}", response_model=ApiResponse, summary="删除会话")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    删除指定会话及其所有Cookie
    """
    success = session_manager.delete_session(current_user.username, session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
    
    return ApiResponse(
        success=True,
        message="会话已删除",
        data={"session_id": session_id}
    )


@router.delete("/clear", response_model=ApiResponse, summary="清除所有会话")
async def clear_sessions(
    current_user: User = Depends(get_current_active_user)
):
    """
    清除当前用户的所有会话
    """
    count = session_manager.clear_user_sessions(current_user.username)
    
    return ApiResponse(
        success=True,
        message=f"已清除 {count} 个会话",
        data={"cleared_count": count}
    )
