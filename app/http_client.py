"""
HTTP客户端 - 封装httpx实现HTTP请求
"""
import time
import asyncio
from typing import Optional, Dict, Any, List
import httpx

from .config import settings
from .models import HttpRequest, HttpResponse, HttpMethod
from .session_manager import session_manager, SessionData


class HttpClient:
    """HTTP客户端"""
    
    def __init__(self):
        self.default_headers = {
            "User-Agent": settings.HTTP_USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
        }
    
    async def request(self, req: HttpRequest, user: str) -> HttpResponse:
        """执行HTTP请求"""
        start_time = time.time()
        
        # 获取或创建会话
        session_data: Optional[SessionData] = None
        if req.session_id:
            session_data = session_manager.get_session(user, req.session_id, auto_create=True)
        
        # 构建请求头
        headers = {**self.default_headers}
        if req.headers:
            headers.update(req.headers)
        
        # 构建Cookie
        cookies = {}
        if session_data:
            cookies.update(session_data.get_cookies(req.url))
        if req.cookies:
            cookies.update(req.cookies)
        
        # 构建代理
        proxies = None
        if req.proxy:
            proxies = {"http://": req.proxy, "https://": req.proxy}
        
        # 构建请求参数
        request_kwargs = {
            "method": req.method.value,
            "url": req.url,
            "headers": headers,
            "cookies": cookies if cookies else None,
            "params": req.params,
            "timeout": req.timeout or settings.HTTP_TIMEOUT,
            "follow_redirects": req.follow_redirects,
        }
        
        # 处理请求体
        if req.json_data:
            request_kwargs["json"] = req.json_data
        elif req.data:
            # 判断是否为JSON
            data = req.data.strip()
            if data.startswith('{') or data.startswith('['):
                request_kwargs["content"] = data
                if "Content-Type" not in headers:
                    request_kwargs["headers"]["Content-Type"] = "application/json"
            else:
                request_kwargs["content"] = data
                if "Content-Type" not in headers:
                    request_kwargs["headers"]["Content-Type"] = "application/x-www-form-urlencoded"
        
        # 执行请求
        async with httpx.AsyncClient(
            verify=req.verify_ssl,
            proxies=proxies,
            max_redirects=settings.HTTP_MAX_REDIRECTS
        ) as client:
            response = await client.request(**request_kwargs)
        
        # 保存Cookie到会话
        if session_data and req.save_cookies:
            session_data.merge_response_cookies(response)
        
        # 计算耗时
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # 解析JSON响应
        json_data = None
        try:
            json_data = response.json()
        except:
            pass
        
        # 构建响应
        return HttpResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            cookies=dict(response.cookies),
            text=response.text,
            json_data=json_data,
            elapsed_ms=elapsed_ms,
            final_url=str(response.url)
        )
    
    async def batch_request(
        self, 
        requests: List[HttpRequest], 
        user: str, 
        parallel: bool = False
    ) -> List[HttpResponse]:
        """批量请求"""
        if parallel:
            # 并行执行
            tasks = [self.request(req, user) for req in requests]
            return await asyncio.gather(*tasks)
        else:
            # 串行执行
            results = []
            for req in requests:
                result = await self.request(req, user)
                results.append(result)
            return results


# 全局HTTP客户端实例
http_client = HttpClient()
