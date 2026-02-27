"""
API测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8080"

def test_api():
    print("=" * 50)
    print("XiaoHaoJi API 测试")
    print("=" * 50)
    
    # 1. 测试首页
    print("\n[1] 测试首页...")
    resp = requests.get(f"{BASE_URL}/")
    print(f"    状态: {resp.status_code}")
    print(f"    响应: {resp.json()}")
    
    # 2. 登录获取Token
    print("\n[2] 登录获取Token...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    print(f"    状态: {resp.status_code}")
    token = resp.json().get("access_token")
    print(f"    Token: {token[:50]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. 创建会话
    print("\n[3] 创建会话...")
    resp = requests.post(f"{BASE_URL}/session/create", 
        headers=headers,
        json={"session_id": "test-account"}
    )
    print(f"    状态: {resp.status_code}")
    print(f"    响应: {resp.json()}")
    
    # 4. 发送GET请求
    print("\n[4] 发送GET请求...")
    resp = requests.post(f"{BASE_URL}/http/request",
        headers=headers,
        json={
            "url": "https://httpbin.org/get?name=xiaohao",
            "method": "GET",
            "session_id": "test-account"
        }
    )
    print(f"    状态: {resp.status_code}")
    data = resp.json()
    print(f"    HTTP状态码: {data.get('status_code')}")
    print(f"    耗时: {data.get('elapsed_ms')}ms")
    print(f"    响应Cookie: {data.get('cookies')}")
    
    # 5. 发送POST请求
    print("\n[5] 发送POST请求...")
    resp = requests.post(f"{BASE_URL}/http/request",
        headers=headers,
        json={
            "url": "https://httpbin.org/post",
            "method": "POST",
            "data": "username=test&password=123456",
            "session_id": "test-account"
        }
    )
    print(f"    状态: {resp.status_code}")
    data = resp.json()
    print(f"    HTTP状态码: {data.get('status_code')}")
    print(f"    耗时: {data.get('elapsed_ms')}ms")
    
    # 6. 设置Cookie
    print("\n[6] 设置Cookie...")
    resp = requests.post(f"{BASE_URL}/cookie/set",
        headers=headers,
        json={
            "session_id": "test-account",
            "url": "https://example.com",
            "cookies": {
                "session": "abc123",
                "token": "xyz789",
                "user_id": "12345"
            }
        }
    )
    print(f"    状态: {resp.status_code}")
    print(f"    响应: {resp.json()}")
    
    # 7. 获取Cookie
    print("\n[7] 获取Cookie...")
    resp = requests.get(f"{BASE_URL}/cookie/get/test-account",
        headers=headers
    )
    print(f"    状态: {resp.status_code}")
    print(f"    Cookie: {resp.json()}")
    
    # 8. 带Cookie请求
    print("\n[8] 带Cookie请求验证...")
    resp = requests.post(f"{BASE_URL}/http/request",
        headers=headers,
        json={
            "url": "https://httpbin.org/cookies",
            "method": "GET",
            "session_id": "test-account"
        }
    )
    print(f"    状态: {resp.status_code}")
    data = resp.json()
    print(f"    服务器看到的Cookie: {data.get('json_data', {}).get('cookies', {})}")
    
    # 9. 列出所有会话
    print("\n[9] 列出所有会话...")
    resp = requests.get(f"{BASE_URL}/session/list", headers=headers)
    print(f"    状态: {resp.status_code}")
    sessions = resp.json()
    print(f"    会话数量: {sessions.get('total')}")
    for s in sessions.get('sessions', []):
        print(f"    - {s.get('session_id')}: {s.get('cookie_count')} cookies")
    
    # 10. 批量请求
    print("\n[10] 批量请求(并行)...")
    resp = requests.post(f"{BASE_URL}/http/batch",
        headers=headers,
        json={
            "requests": [
                {"url": "https://httpbin.org/get", "method": "GET"},
                {"url": "https://httpbin.org/ip", "method": "GET"},
                {"url": "https://httpbin.org/user-agent", "method": "GET"}
            ],
            "parallel": True
        }
    )
    print(f"    状态: {resp.status_code}")
    data = resp.json()
    print(f"    总耗时: {data.get('total_elapsed_ms')}ms")
    print(f"    请求数: {len(data.get('results', []))}")
    
    print("\n" + "=" * 50)
    print("所有测试完成!")
    print("=" * 50)
    print(f"\nSwagger文档: {BASE_URL}/docs")
    print(f"ReDoc文档: {BASE_URL}/redoc")


if __name__ == "__main__":
    test_api()
