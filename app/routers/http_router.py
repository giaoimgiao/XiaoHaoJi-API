"""
HTTP请求路由
"""
import time
from fastapi import APIRouter, Depends, HTTPException

from ..models import (
    HttpRequest, HttpResponse, 
    BatchRequest, BatchResponse,
    ApiResponse, User
)
from ..auth import get_current_active_user
from ..http_client import http_client

router = APIRouter(prefix="/http", tags=["HTTP请求"])


@router.post("/request", response_model=HttpResponse, summary="发送HTTP请求")
async def send_request(
    req: HttpRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    发送HTTP请求
    
    支持功能:
    - GET/POST/PUT/DELETE等方法
    - 自定义Headers
    - Cookie自动管理(通过session_id)
    - 代理支持
    - 自动跟随重定向
    
    **示例 - GET请求:**
    ```json
    {
        "url": "https://httpbin.org/get",
        "method": "GET",
        "session_id": "my-session"
    }
    ```
    
    **示例 - POST JSON:**
    ```json
    {
        "url": "https://httpbin.org/post",
        "method": "POST",
        "json_data": {"name": "test", "value": 123},
        "session_id": "my-session"
    }
    ```
    
    **示例 - POST表单:**
    ```json
    {
        "url": "https://httpbin.org/post",
        "method": "POST",
        "data": "username=test&password=123",
        "session_id": "my-session"
    }
    ```
    """
    try:
        return await http_client.request(req, current_user.username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


@router.post("/get", response_model=HttpResponse, summary="GET请求(简化)")
async def get_request(
    url: str,
    session_id: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    简化的GET请求
    
    - **url**: 请求URL
    - **session_id**: 会话ID(可选)
    """
    req = HttpRequest(url=url, session_id=session_id)
    try:
        return await http_client.request(req, current_user.username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


@router.post("/post", response_model=HttpResponse, summary="POST请求(简化)")
async def post_request(
    url: str,
    data: str = None,
    session_id: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    简化的POST请求
    
    - **url**: 请求URL
    - **data**: POST数据
    - **session_id**: 会话ID(可选)
    """
    from ..models import HttpMethod
    req = HttpRequest(url=url, method=HttpMethod.POST, data=data, session_id=session_id)
    try:
        return await http_client.request(req, current_user.username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"请求失败: {str(e)}")


@router.post("/batch", response_model=BatchResponse, summary="批量请求")
async def batch_request(
    batch: BatchRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    批量发送HTTP请求
    
    - **requests**: 请求列表
    - **parallel**: 是否并行执行(默认串行)
    
    **示例:**
    ```json
    {
        "requests": [
            {"url": "https://httpbin.org/get", "method": "GET"},
            {"url": "https://httpbin.org/post", "method": "POST", "data": "test=1"}
        ],
        "parallel": true
    }
    ```
    """
    start_time = time.time()
    
    try:
        results = await http_client.batch_request(
            batch.requests, 
            current_user.username, 
            batch.parallel
        )
        
        total_elapsed = int((time.time() - start_time) * 1000)
        
        return BatchResponse(results=results, total_elapsed_ms=total_elapsed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量请求失败: {str(e)}")
