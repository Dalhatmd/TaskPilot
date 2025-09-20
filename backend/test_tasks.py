#!/usr/bin/env python3
"""
Test script for task endpoints.
Tests task CRUD operations and task management features.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Global variables to store auth token and user info
auth_token = None
user_id = None


def authenticate():
    """Authenticate and get access token."""
    global auth_token, user_id
    
    print("🔐 Authenticating...")
    
    # Try to login first
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
        
        if response.status_code == 200:
            data = response.json()
            auth_token = data["access_token"]
            user_id = data["user"]["id"]
            print("✅ Login successful!")
            return True
    except Exception as e:
        print(f"❌ Login failed: {e}")
    
    # If login fails, try to signup
    print("📝 Attempting signup...")
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
        
        if response.status_code == 201:
            data = response.json()
            auth_token = data["access_token"]
            user_id = data["user"]["id"]
            print("✅ Signup successful!")
            return True
        else:
            print(f"❌ Signup failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return False


def get_headers():
    """Get headers with authentication token."""
    if not auth_token:
        raise Exception("Not authenticated. Call authenticate() first.")
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


def test_create_task():
    """Test creating a new task."""
    print("\n📝 Testing task creation...")
    
    task_data = {
        "title": "Complete project documentation",
        "description": "Write comprehensive documentation for the TaskPilot API",
        "status": "todo",
        "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "priority": "high"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/tasks/",
            json=task_data,
            headers=get_headers()
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201:
            task = response.json()
            print("✅ Task created successfully!")
            print(f"   Task ID: {task['id']}")
            print(f"   Title: {task['title']}")
            print(f"   Status: {task['status']}")
            return task
        else:
            print(f"❌ Task creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Task creation error: {e}")
        return None


def test_get_tasks():
    """Test getting tasks list."""
    print("\n📋 Testing get tasks...")
    
    try:
        response = requests.get(
            f"{API_BASE}/tasks/",
            headers=get_headers()
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Tasks retrieved successfully!")
            print(f"   Total tasks: {data['total']}")
            print(f"   Page: {data['page']} of {data['pages']}")
            for task in data['tasks']:
                print(f"   - {task['title']} ({task['status']})")
            return data
        else:
            print(f"❌ Get tasks failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Get tasks error: {e}")
        return None


def test_get_task(task_id: int):
    """Test getting a specific task."""
    print(f"\n🔍 Testing get task {task_id}...")
    
    try:
        response = requests.get(
            f"{API_BASE}/tasks/{task_id}",
            headers=get_headers()
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            task = response.json()
            print("✅ Task retrieved successfully!")
            print(f"   Title: {task['title']}")
            print(f"   Description: {task['description']}")
            print(f"   Status: {task['status']}")
            print(f"   Priority: {task['priority']}")
            return task
        else:
            print(f"❌ Get task failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Get task error: {e}")
        return None


def test_update_task(task_id: int):
    """Test updating a task."""
    print(f"\n✏️ Testing update task {task_id}...")
    
    update_data = {
        "status": "in_progress",
        "description": "Updated: Write comprehensive documentation for the TaskPilot API with examples"
    }
    
    try:
        response = requests.put(
            f"{API_BASE}/tasks/{task_id}",
            json=update_data,
            headers=get_headers()
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            task = response.json()
            print("✅ Task updated successfully!")
            print(f"   New status: {task['status']}")
            print(f"   Updated description: {task['description']}")
            return task
        else:
            print(f"❌ Update task failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Update task error: {e}")
        return None


def test_update_task_status(task_id: int):
    """Test updating only task status."""
    print(f"\n🔄 Testing update task status {task_id}...")
    
    status_data = {
        "status": "completed"
    }
    
    try:
        response = requests.patch(
            f"{API_BASE}/tasks/{task_id}/status",
            json=status_data,
            headers=get_headers()
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            task = response.json()
            print("✅ Task status updated successfully!")
            print(f"   New status: {task['status']}")
            return task
        else:
            print(f"❌ Update task status failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Update task status error: {e}")
        return None


def test_get_tasks_by_status():
    """Test getting tasks by status."""
    print("\n📊 Testing get tasks by status...")
    
    try:
        response = requests.get(
            f"{API_BASE}/tasks/status/completed",
            headers=get_headers()
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            tasks = response.json()
            print("✅ Tasks by status retrieved successfully!")
            print(f"   Found {len(tasks)} completed tasks")
            for task in tasks:
                print(f"   - {task['title']} ({task['status']})")
            return tasks
        else:
            print(f"❌ Get tasks by status failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Get tasks by status error: {e}")
        return None


def test_delete_task(task_id: int):
    """Test deleting a task."""
    print(f"\n🗑️ Testing delete task {task_id}...")
    
    try:
        response = requests.delete(
            f"{API_BASE}/tasks/{task_id}",
            headers=get_headers()
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 204:
            print("✅ Task deleted successfully!")
            return True
        else:
            print(f"❌ Delete task failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Delete task error: {e}")
        return False


def main():
    """Run all task tests."""
    print("🚀 Starting TaskPilot Task Tests")
    print("=" * 50)
    
    # Authenticate first
    if not authenticate():
        print("❌ Authentication failed. Exiting.")
        return
    
    # Test task operations
    created_task = test_create_task()
    if not created_task:
        print("❌ Task creation failed. Exiting.")
        return
    
    task_id = created_task['id']
    
    # Test other operations
    test_get_tasks()
    test_get_task(task_id)
    test_update_task(task_id)
    test_update_task_status(task_id)
    test_get_tasks_by_status()
    
    # Create a few more tasks for testing
    print("\n📝 Creating additional tasks...")
    for i in range(2):
        task_data = {
            "title": f"Task {i+2}",
            "description": f"Description for task {i+2}",
            "status": "todo",
            "priority": "medium"
        }
        try:
            response = requests.post(
                f"{API_BASE}/tasks/",
                json=task_data,
                headers=get_headers()
            )
            if response.status_code == 201:
                print(f"   ✅ Created task {i+2}")
        except Exception as e:
            print(f"   ❌ Failed to create task {i+2}: {e}")
    
    # Test getting all tasks again
    test_get_tasks()
    
    # Test delete (optional - comment out if you want to keep the task)
    # test_delete_task(task_id)
    
    print("\n" + "=" * 50)
    print("🏁 Task tests completed!")


if __name__ == "__main__":
    main()
