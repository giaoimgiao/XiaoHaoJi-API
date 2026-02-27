"""
会话管理器 - 管理多个独立的Cookie会话
"""
import uuid
from datetime import datetime
from typing import Dict, Optional, List
from collections import defaultdict
import httpx


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        # 存储结构: {user: {session_id: SessionData}}
        self._sessions: Dict[str, Dict[str, 'SessionData']] = defaultdict(dict)
    
    def create_session(self, user: str, session_id: Optional[str] = None) -> str:
        """创建新会话"""
        if session_id is None:
            session_id = str(uuid.uuid4())[:8]
        
        if session_id in self._sessions[user]:
            raise ValueError(f"会话 {session_id} 已存在")
        
        self._sessions[user][session_id] = SessionData(session_id)
        return session_id
    
    def get_session(self, user: str, session_id: str, auto_create: bool = True) -> Optional['SessionData']:
        """获取会话"""
        if session_id not in self._sessions[user]:
            if auto_create:
                self.create_session(user, session_id)
            else:
                return None
        return self._sessions[user].get(session_id)
    
    def delete_session(self, user: str, session_id: str) -> bool:
        """删除会话"""
        if session_id in self._sessions[user]:
            del self._sessions[user][session_id]
            return True
        return False
    
    def list_sessions(self, user: str) -> List[dict]:
        """列出用户所有会话"""
        sessions = []
        for session_id, session_data in self._sessions[user].items():
            sessions.append(session_data.to_dict())
        return sessions
    
    def clear_user_sessions(self, user: str) -> int:
        """清除用户所有会话"""
        count = len(self._sessions[user])
        self._sessions[user].clear()
        return count


class SessionData:
    """单个会话数据"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        # 按域名存储Cookie: {domain: {name: value}}
        self._cookies: Dict[str, Dict[str, str]] = defaultdict(dict)
    
    def update_last_used(self):
        """更新最后使用时间"""
        self.last_used = datetime.now()
    
    def set_cookies(self, url: str, cookies: Dict[str, str]):
        """设置Cookie"""
        domain = self._extract_domain(url)
        self._cookies[domain].update(cookies)
        self.update_last_used()
    
    def get_cookies(self, url: Optional[str] = None) -> Dict[str, str]:
        """获取Cookie"""
        self.update_last_used()
        
        if url is None:
            # 返回所有Cookie
            all_cookies = {}
            for domain_cookies in self._cookies.values():
                all_cookies.update(domain_cookies)
            return all_cookies
        
        # 返回指定域名的Cookie
        domain = self._extract_domain(url)
        result = {}
        
        for stored_domain, cookies in self._cookies.items():
            # 匹配域名 (支持子域名匹配)
            if domain.endswith(stored_domain) or stored_domain.endswith(domain):
                result.update(cookies)
            elif stored_domain.startswith('.') and domain.endswith(stored_domain[1:]):
                result.update(cookies)
        
        return result
    
    def clear_cookies(self, url: Optional[str] = None):
        """清除Cookie"""
        if url is None:
            self._cookies.clear()
        else:
            domain = self._extract_domain(url)
            if domain in self._cookies:
                del self._cookies[domain]
        self.update_last_used()
    
    def get_cookies_by_domain(self) -> Dict[str, Dict[str, str]]:
        """按域名获取所有Cookie"""
        return dict(self._cookies)
    
    def merge_response_cookies(self, response: httpx.Response):
        """从响应中合并Cookie"""
        url = str(response.url)
        cookies = dict(response.cookies)
        if cookies:
            self.set_cookies(url, cookies)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat(),
            "cookie_count": sum(len(c) for c in self._cookies.values()),
            "cookies": self.get_cookies_by_domain()
        }
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """提取域名"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc or url


# 全局会话管理器实例
session_manager = SessionManager()
