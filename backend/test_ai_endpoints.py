"""
Tests for AI API endpoints.
Tests the FastAPI endpoints for AI-powered task summarization.
"""

import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import the FastAPI app
from app.main import app
from app.api.v1.endpoints.ai import TaskInput

# Create test client
client = TestClient(app)


class TestAIEndpoints:
    """Test cases for AI API endpoints."""

    def test_summarize_tasks_endpoint_success(self):
        """Test successful task summarization via API endpoint."""
        
        # Sample task data
        task_data = [
            {
                "title": "Complete project proposal",
                "description": "Write and submit the quarterly project proposal by Friday",
                "due_date": "2025-09-25",
                "status": "TODO"
            },
            {
                "title": "Review code changes",
                "description": "Review pull requests and provide feedback to team members",
                "due_date": None,
                "status": "IN_PROGRESS"
            }
        ]

        # Mock the AI service response
        with patch('app.api.v1.endpoints.ai.summarize_tasks') as mock_summarize:
            mock_summarize.return_value = "Summary: You have 2 main tasks focusing on project completion and code review."
            
            # Make POST request to the endpoint
            response = client.post("/api/v1/ai/summarize-tasks", json=task_data)
            
            # Verify response
            assert response.status_code == 200
            response_data = response.json()
            assert "summary" in response_data
            assert response_data["summary"] == "Summary: You have 2 main tasks focusing on project completion and code review."
            
            # Verify the AI service was called correctly
            mock_summarize.assert_called_once()
            call_args = mock_summarize.call_args[0][0]
            assert len(call_args) == 2
            assert call_args[0]["title"] == "Complete project proposal"
            assert call_args[1]["title"] == "Review code changes"

    def test_summarize_tasks_endpoint_empty_list(self):
        """Test endpoint with empty task list."""
        
        task_data = []

        with patch('app.api.v1.endpoints.ai.summarize_tasks') as mock_summarize:
            mock_summarize.return_value = "No tasks to summarize."
            
            response = client.post("/api/v1/ai/summarize-tasks", json=task_data)
            
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["summary"] == "No tasks to summarize."
            
            mock_summarize.assert_called_once_with([])

    def test_summarize_tasks_endpoint_single_task(self):
        """Test endpoint with single task."""
        
        task_data = [
            {
                "title": "Fix critical bug",
                "description": "Resolve the authentication issue in production ASAP",
                "due_date": "2025-09-22",
                "status": "TODO"
            }
        ]

        with patch('app.api.v1.endpoints.ai.summarize_tasks') as mock_summarize:
            mock_summarize.return_value = "Critical task: Fix authentication bug in production immediately."
            
            response = client.post("/api/v1/ai/summarize-tasks", json=task_data)
            
            assert response.status_code == 200
            response_data = response.json()
            assert "Critical task:" in response_data["summary"]

    def test_summarize_tasks_endpoint_ai_service_error(self):
        """Test endpoint when AI service raises an exception."""
        
        task_data = [
            {
                "title": "Test task",
                "description": "Test description",
                "due_date": None,
                "status": "TODO"
            }
        ]

        with patch('app.api.v1.endpoints.ai.summarize_tasks') as mock_summarize:
            mock_summarize.side_effect = Exception("AI API connection failed")
            
            response = client.post("/api/v1/ai/summarize-tasks", json=task_data)
            
            assert response.status_code == 200  # Endpoint handles errors gracefully
            response_data = response.json()
            assert "error" in response_data
            assert "AI API connection failed" in response_data["error"]

    def test_summarize_tasks_endpoint_invalid_json(self):
        """Test endpoint with invalid JSON data."""
        
        # Invalid data - missing required fields
        invalid_data = [
            {
                "title": "Valid task",
                # Missing description
                "due_date": "2025-09-25"
            }
        ]

        response = client.post("/api/v1/ai/summarize-tasks", json=invalid_data)
        
        # Should return validation error
        assert response.status_code == 422  # Unprocessable Entity

    def test_summarize_tasks_endpoint_malformed_request(self):
        """Test endpoint with completely malformed request."""
        
        # Send non-list data
        invalid_data = {"not": "a list"}

        response = client.post("/api/v1/ai/summarize-tasks", json=invalid_data)
        
        # Should return validation error
        assert response.status_code == 422

    def test_task_input_model_validation(self):
        """Test TaskInput model validation."""
        
        # Valid task input
        valid_task = TaskInput(
            title="Test task",
            description="Test description",
            due_date="2025-09-25"
        )
        assert valid_task.title == "Test task"
        assert valid_task.description == "Test description"
        assert valid_task.due_date == "2025-09-25"
        
        # Valid task without due_date
        task_no_date = TaskInput(
            title="Test task",
            description="Test description"
        )
        assert task_no_date.due_date is None

    def test_summarize_tasks_endpoint_with_special_characters(self):
        """Test endpoint with tasks containing special characters."""
        
        task_data = [
            {
                "title": "Update API & documentation",
                "description": "Fix API endpoints (v2.0) & update docs with new schema",
                "due_date": "2025-09-30",
                "status": "IN_PROGRESS"
            },
            {
                "title": "Test: E2E scenarios",
                "description": "Run end-to-end tests for user registration/login flow",
                "due_date": None,
                "status": "TODO"
            }
        ]

        with patch('app.api.v1.endpoints.ai.summarize_tasks') as mock_summarize:
            mock_summarize.return_value = "Tasks involve API updates and testing procedures."
            
            response = client.post("/api/v1/ai/summarize-tasks", json=task_data)
            
            assert response.status_code == 200
            response_data = response.json()
            assert "summary" in response_data
            
            # Verify special characters were passed correctly
            call_args = mock_summarize.call_args[0][0]
            assert "&" in call_args[0]["title"]
            assert "(" in call_args[0]["description"]
            assert "/" in call_args[1]["description"]

    def test_summarize_tasks_endpoint_large_task_list(self):
        """Test endpoint with a large number of tasks."""
        
        # Create 10 tasks
        task_data = []
        statuses = ["TODO", "IN_PROGRESS", "TODO", "IN_PROGRESS", "TODO"]
        for i in range(10):
            task_data.append({
                "title": f"Task {i+1}",
                "description": f"Description for task {i+1}",
                "due_date": f"2025-09-{20+i}",
                "status": statuses[i % len(statuses)]
            })

        with patch('app.api.v1.endpoints.ai.summarize_tasks') as mock_summarize:
            mock_summarize.return_value = "Summary of 10 tasks with various objectives and deadlines."
            
            response = client.post("/api/v1/ai/summarize-tasks", json=task_data)
            
            assert response.status_code == 200
            response_data = response.json()
            assert "summary" in response_data
            
            # Verify all tasks were passed to AI service
            call_args = mock_summarize.call_args[0][0]
            assert len(call_args) == 10
            assert call_args[0]["title"] == "Task 1"
            assert call_args[9]["title"] == "Task 10"

    def test_summarize_tasks_endpoint_with_status(self):
        """Test endpoint with different task statuses."""
        
        task_data = [
            {
                "title": "Completed task",
                "description": "This task is already done",
                "due_date": "2025-09-20",
                "status": "COMPLETED"
            },
            {
                "title": "In progress task", 
                "description": "This task is being worked on",
                "due_date": "2025-09-25",
                "status": "IN_PROGRESS"
            },
            {
                "title": "Todo task",
                "description": "This task hasn't been started",
                "due_date": "2025-09-30",
                "status": "TODO"
            }
        ]

        with patch('app.api.v1.endpoints.ai.summarize_tasks') as mock_summarize:
            mock_summarize.return_value = "You have 1 completed task, 1 in progress, and 1 pending task."
            
            response = client.post("/api/v1/ai/summarize-tasks", json=task_data)
            
            assert response.status_code == 200
            response_data = response.json()
            assert "summary" in response_data
            
            # Verify status information was passed correctly
            call_args = mock_summarize.call_args[0][0]
            assert len(call_args) == 3
            assert call_args[0]["status"] == "COMPLETED"
            assert call_args[1]["status"] == "IN_PROGRESS"
            assert call_args[2]["status"] == "TODO"


def main():
    """Run all tests manually."""
    print("Starting AI Endpoints Tests")
    print("=" * 50)
    
    test_instance = TestAIEndpoints()
    test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            print(f"Running {test_method}...")
            getattr(test_instance, test_method)()
            print(f"✓ {test_method} passed")
            passed += 1
        except Exception as e:
            print(f"❌ {test_method} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())