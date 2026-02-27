# XiaoHaoJi API

HTTP请求代理服务，提供Cookie管理、会话池、请求限流等功能。

## 快速开始

### 1. 安装依赖

```bash
cd XiaoHaoJi-API
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python run.py
```

服务启动后访问:
- API文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc

### 3. 默认账号

- 用户名: `admin`
- 密码: `admin123`

## API接口

### 认证

| 接口 | 方法 | 说明 |
|------|------|------|
| `/auth/login` | POST | 登录获取Token |
| `/auth/info` | GET | 获取API信息 |

### HTTP请求

| 接口 | 方法 | 说明 |
|------|------|------|
| `/http/request` | POST | 发送HTTP请求 |
| `/http/get` | POST | 简化GET请求 |
| `/http/post` | POST | 简化POST请求 |
| `/http/batch` | POST | 批量请求 |

### Cookie管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/cookie/set` | POST | 设置Cookie |
| `/cookie/get` | POST | 获取Cookie |
| `/cookie/get/{session_id}` | GET | 获取Cookie(简化) |
| `/cookie/clear/{session_id}` | DELETE | 清除Cookie |
| `/cookie/all/{session_id}` | GET | 获取所有Cookie |

### 会话管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/session/create` | POST | 创建会话 |
| `/session/list` | GET | 列出所有会话 |
| `/session/get/{session_id}` | GET | 获取会话详情 |
| `/session/delete/{session_id}` | DELETE | 删除会话 |
| `/session/clear` | DELETE | 清除所有会话 |

## 使用示例

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 登录获取Token
resp = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. 创建会话
requests.post(f"{BASE_URL}/session/create", 
    headers=headers,
    json={"session_id": "account-1"}
)

# 3. 发送GET请求
resp = requests.post(f"{BASE_URL}/http/request",
    headers=headers,
    json={
        "url": "https://httpbin.org/get",
        "method": "GET",
        "session_id": "account-1"
    }
)
print(resp.json())

# 4. 发送POST请求(自动保存Cookie)
resp = requests.post(f"{BASE_URL}/http/request",
    headers=headers,
    json={
        "url": "https://httpbin.org/post",
        "method": "POST",
        "data": "username=test&password=123",
        "session_id": "account-1"
    }
)
print(resp.json())

# 5. 获取会话中的Cookie
resp = requests.get(f"{BASE_URL}/cookie/get/account-1", headers=headers)
print(resp.json())

# 6. 手动设置Cookie
requests.post(f"{BASE_URL}/cookie/set",
    headers=headers,
    json={
        "session_id": "account-1",
        "url": "https://example.com",
        "cookies": {"session": "abc123", "token": "xyz"}
    }
)

# 7. 批量请求
resp = requests.post(f"{BASE_URL}/http/batch",
    headers=headers,
    json={
        "requests": [
            {"url": "https://httpbin.org/get", "method": "GET"},
            {"url": "https://httpbin.org/ip", "method": "GET"}
        ],
        "parallel": True
    }
)
print(resp.json())
```

### cURL

```bash
# 登录
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# 发送请求
curl -X POST http://localhost:8000/http/request \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://httpbin.org/get",
    "method": "GET",
    "session_id": "test"
  }'
```

### JavaScript

```javascript
const BASE_URL = "http://localhost:8000";

// 登录
const loginResp = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username: "admin", password: "admin123"})
});
const {access_token} = await loginResp.json();

// 发送请求
const resp = await fetch(`${BASE_URL}/http/request`, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${access_token}`
    },
    body: JSON.stringify({
        url: "https://httpbin.org/get",
        method: "GET",
        session_id: "my-session"
    })
});
console.log(await resp.json());
```

## 配置说明

可通过环境变量或 `.env` 文件配置:

```env
# API密钥
API_SECRET_KEY=your-secret-key

# 管理员账号
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password

# 限流配置
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# HTTP配置
HTTP_TIMEOUT=30
HTTP_USER_AGENT=XiaoHaoJi-API/1.0
```

## 会话池说明

会话池用于管理多个独立的Cookie存储，适用于多账号场景:

1. 每个会话有唯一的 `session_id`
2. 会话之间Cookie完全隔离
3. 请求时指定 `session_id` 自动携带对应Cookie
4. 响应Cookie自动保存到对应会话

**典型场景:**
- 账号1: `session_id: "account-1"`
- 账号2: `session_id: "account-2"`
- 两个账号的Cookie互不影响

## 注意事项

1. 生产环境请修改 `API_SECRET_KEY` 和管理员密码
2. 默认信任所有SSL证书，生产环境建议开启验证
3. 会话数据存储在内存中，重启后丢失
4. 如需持久化，可配置Redis
