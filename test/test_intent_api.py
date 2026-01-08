import requests
import json

def test_intent_analyze():
    url = "http://localhost:8000/intent/analyze"
    
    # 正确的请求方式：使用 JSON Body
    payload = {
        "text": "睡不着",
        "user_id": "001"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"正在发送请求到: {url}")
        print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("响应结果:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"请求发生异常: {e}")

if __name__ == "__main__":
    test_intent_analyze()

