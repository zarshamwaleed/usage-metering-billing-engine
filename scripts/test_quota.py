import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time

BASE_URL = "http://host.docker.internal:8000/api/v1"
TENANT_ID = 1

def test_quota():
    print("=" * 60)
    print("QUOTA ENFORCEMENT TEST")
    print("=" * 60)
    
    # First, check current quota
    print("\n📊 Checking current quota...")
    response = requests.get(f"{BASE_URL}/quota/{TENANT_ID}")
    if response.status_code == 200:
        data = response.json()
        print(f"Current API calls: {data['current_usage']['api_calls']}")
        print(f"API limit: {data['limits']['api_calls']}")
        print(f"Remaining: {data['limits']['api_calls'] - data['current_usage']['api_calls']}")
    else:
        print(f"Error: {response.status_code}")
        return
    
    # Generate API calls until we reach quota
    print("\n🚀 Generating API calls...")
    count = 0
    while True:
        count += 1
        test_key = f"quota-test-{int(time.time())}-{count}"
        headers = {
            "Content-Type": "application/json",
            "idempotency-key": test_key
        }
        payload = {"input_tokens": 1}
        
        response = requests.post(
            f"{BASE_URL}/generate?tenant_id={TENANT_ID}",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"  Request {count}: ✅ Allowed")
        elif response.status_code == 429:
            print(f"  Request {count}: 🚫 Blocked - Quota exceeded!")
            print(f"  Response: {response.json()}")
            break
        else:
            print(f"  Request {count}: ❌ Error {response.status_code}")
            print(f"  Response: {response.text}")
            break
    
    print("\n" + "=" * 60)
    print(f"📊 Total requests made: {count}")
    print("=" * 60)

if __name__ == "__main__":
    test_quota()
