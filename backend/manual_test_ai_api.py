"""
Manual API test for AI endpoints.
Shows how to test the actual HTTP endpoint manually.
"""

import sys
import os
import json
import requests

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))


def test_api_endpoint_manually():
    """Test the actual API endpoint with HTTP requests."""
    
    print("Testing AI summarization endpoint manually...")
    
    # API endpoint URL (assumes FastAPI is running on localhost:8000)
    url = "http://127.0.0.1:8000/api/v1/ai/summarize-tasks"
    
    # Sample task data
    task_data = [
        {
            "title": "Complete project proposal",
            "description": "Write and submit the quarterly project proposal by Friday",
            "due_date": "2025-09-25"
        },
        {
            "title": "Review code changes",
            "description": "Review pull requests and provide feedback to team members",
            "due_date": None
        },
        {
            "title": "Prepare client presentation",
            "description": "Create slides for Monday client meeting about new features",
            "due_date": "2025-09-28"
        }
    ]
    
    try:
        # Make POST request
        print("Sending POST request to:", url)
        print("Task data:", json.dumps(task_data, indent=2))
        
        response = requests.post(
            url,
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            
            if "summary" in result:
                print("📝 AI Summary:")
                print("-" * 50)
                print(result["summary"])
                print("-" * 50)
            elif "error" in result:
                print("⚠️  API returned an error:")
                print(result["error"])
            
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print("Response:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure FastAPI server is running on http://127.0.0.1:8000")
        print("Run: uvicorn app.main:app --reload")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True


def test_api_endpoint_edge_cases():
    """Test edge cases with the API endpoint."""
    
    print("\nTesting edge cases...")
    
    base_url = "http://127.0.0.1:8000/api/v1/ai/summarize-tasks"
    
    # Test 1: Empty task list
    print("\n1. Testing empty task list...")
    try:
        response = requests.post(base_url, json=[])
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Empty list result: {result}")
        else:
            print(f"✗ Empty list failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Empty list test failed: {e}")
    
    # Test 2: Invalid data
    print("\n2. Testing invalid data...")
    try:
        invalid_data = [{"title": "Missing description"}]  # Missing required 'description'
        response = requests.post(base_url, json=invalid_data)
        print(f"✓ Invalid data response: {response.status_code} (expected 422)")
    except Exception as e:
        print(f"✗ Invalid data test failed: {e}")
    
    # Test 3: Single task
    print("\n3. Testing single task...")
    try:
        single_task = [{
            "title": "Single task test",
            "description": "Testing with just one task",
            "due_date": "2025-09-25"
        }]
        response = requests.post(base_url, json=single_task)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Single task result: {result.get('summary', result.get('error'))[:100]}...")
        else:
            print(f"✗ Single task failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Single task test failed: {e}")


def main():
    """Run manual API tests."""
    print("AI Endpoints Manual API Test")
    print("=" * 40)
    print("This test requires FastAPI server to be running!")
    print("Start with: uvicorn app.main:app --reload")
    print("=" * 40)
    
    success = test_api_endpoint_manually()
    
    if success:
        test_api_endpoint_edge_cases()
        print("\n" + "=" * 40)
        print("✅ Manual API tests completed!")
    else:
        print("\n" + "=" * 40)
        print("❌ Manual API tests failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())