import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time

# Use the host's network from inside the container
BASE_URL = "http://host.docker.internal:8000/api/v1"
# Or if running locally: "http://localhost:8000/api/v1"
TENANT_ID = 1

def test_idempotency():
    print("=" * 60)
    print("IDEMPOTENCY TEST")
    print("=" * 60)
    
    # Test data
    test_key = f"idempotency-test-{int(time.time())}"
    payload = {
        "input_tokens": 100,
        "cached_input_tokens": 50,
        "output_tokens": 75,
        "reasoning_tokens": 25
    }
    
    headers = {
        "Content-Type": "application/json",
        "idempotency-key": test_key
    }
    
    print(f"\n📝 Test Key: {test_key}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    # First Request
    print("\n" + "-" * 40)
    print("🚀 FIRST REQUEST (Should record usage)")
    print("-" * 40)
    
    try:
        response1 = requests.post(
            f"{BASE_URL}/generate?tenant_id={TENANT_ID}",
            json=payload,
            headers=headers,
            timeout=5
        )
        
        print(f"Status Code: {response1.status_code}")
        print(f"Response: {json.dumps(response1.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the API is running on http://localhost:8000")
        return
    
    # Second Request (Duplicate)
    print("\n" + "-" * 40)
    print("🔄 SECOND REQUEST (Should return duplicate)")
    print("-" * 40)
    
    try:
        response2 = requests.post(
            f"{BASE_URL}/generate?tenant_id={TENANT_ID}",
            json=payload,
            headers=headers,
            timeout=5
        )
        
        print(f"Status Code: {response2.status_code}")
        print(f"Response: {json.dumps(response2.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Verify results
    print("\n" + "-" * 40)
    print("📊 VERIFICATION")
    print("-" * 40)
    
    if response1.status_code == 200 and response2.status_code == 200:
        data1 = response1.json()
        data2 = response2.json()
        
        if data1.get("status") == "recorded" and data2.get("status") == "duplicate":
            print("✅ IDEMPOTENCY TEST PASSED!")
            print(f"   First request: {data1.get('status')}")
            print(f"   Second request: {data2.get('status')}")
            print(f"   Total tokens recorded: {data1.get('quantity')}")
        else:
            print("❌ IDEMPOTENCY TEST FAILED!")
            print(f"   First request status: {data1.get('status')}")
            print(f"   Second request status: {data2.get('status')}")
    else:
        print("❌ IDEMPOTENCY TEST FAILED!")
        print(f"   First request status code: {response1.status_code}")
        print(f"   Second request status code: {response2.status_code}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_idempotency()
