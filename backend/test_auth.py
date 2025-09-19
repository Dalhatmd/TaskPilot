#!/usr/bin/env python3
"""
Simple test script for authentication endpoints.
Tests signup and login functionality.
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_signup() -> Dict[str, Any]:
    """Test user signup endpoint."""
    print("Testing user signup...")
    
    signup_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "username": "testuser",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Signup successful!")
            return response.json()
        else:
            print("❌ Signup failed!")
            return {}
            
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return {}


def test_login() -> Dict[str, Any]:
    """Test user login endpoint."""
    print("\nTesting user login...")
    
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json()
        else:
            print("❌ Login failed!")
            return {}
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return {}


def test_me_endpoint(access_token: str) -> None:
    """Test /me endpoint with authentication."""
    print("\nTesting /me endpoint...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE}/auth/me",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ /me endpoint successful!")
        else:
            print("❌ /me endpoint failed!")
            
    except Exception as e:
        print(f"❌ /me endpoint error: {e}")


def main():
    """Run all authentication tests."""
    print("🚀 Starting TaskPilot Authentication Tests")
    print("=" * 50)
    
    # Test signup
    signup_result = test_signup()
    
    if signup_result and "access_token" in signup_result:
        access_token = signup_result["access_token"]
        
        # Test /me endpoint
        test_me_endpoint(access_token)
    
    # Test login
    login_result = test_login()
    
    if login_result and "access_token" in login_result:
        access_token = login_result["access_token"]
        
        # Test /me endpoint again
        test_me_endpoint(access_token)
    
    print("\n" + "=" * 50)
    print("🏁 Authentication tests completed!")


if __name__ == "__main__":
    main()
