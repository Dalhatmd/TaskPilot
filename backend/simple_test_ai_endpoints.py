"""
Simple test for AI endpoints without FastAPI TestClient dependency.
Tests the endpoint logic directly.
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from app.api.v1.endpoints.ai import summarize_tasks_endpoint, TaskInput


def test_summarize_tasks_endpoint_basic():
    """Test the endpoint function directly."""
    print("Running test_summarize_tasks_endpoint_basic...")
    
    # Create TaskInput objects
    tasks = [
        TaskInput(
            title="Complete project proposal",
            description="Write and submit the quarterly project proposal by Friday",
            due_date="2025-09-25"
        ),
        TaskInput(
            title="Review code changes",
            description="Review pull requests and provide feedback to team members",
            due_date=None
        )
    ]

    # Mock the summarize_tasks function
    with patch('app.api.v1.endpoints.ai.summarize_tasks') as mock_summarize:
        mock_summarize.return_value = "Summary: You have 2 main tasks focusing on project completion and code review."
        
        # Call the endpoint function directly
        result = summarize_tasks_endpoint(tasks)
        
        # Verify the result
        assert "summary" in result
        assert result["summary"] == "Summary: You have 2 main tasks focusing on project completion and code review."
        
        # Verify the function was called with correct data
        mock_summarize.assert_called_once()
        call_args = mock_summarize.call_args[0][0]
        assert len(call_args) == 2
        assert call_args[0]["title"] == "Complete project proposal"
        assert call_args[1]["title"] == "Review code changes"
        
        print("✓ Basic endpoint test passed")


def test_summarize_tasks_endpoint_error_handling():
    """Test endpoint error handling."""
    print("Running test_summarize_tasks_endpoint_error_handling...")
    
    tasks = [
        TaskInput(
            title="Test task",
            description="Test description",
            due_date=None
        )
    ]

    # Mock the summarize_tasks function to raise an exception
    with patch('app.api.v1.endpoints.ai.summarize_tasks') as mock_summarize:
        mock_summarize.side_effect = Exception("AI API connection failed")
        
        # Call the endpoint function
        result = summarize_tasks_endpoint(tasks)
        
        # Verify error handling
        assert "error" in result
        assert "AI API connection failed" in result["error"]
        
        print("✓ Error handling test passed")


def test_summarize_tasks_endpoint_empty_list():
    """Test endpoint with empty task list."""
    print("Running test_summarize_tasks_endpoint_empty_list...")
    
    tasks = []

    with patch('app.api.v1.endpoints.ai.summarize_tasks') as mock_summarize:
        mock_summarize.return_value = "No tasks to summarize."
        
        result = summarize_tasks_endpoint(tasks)
        
        assert "summary" in result
        assert result["summary"] == "No tasks to summarize."
        mock_summarize.assert_called_once_with([])
        
        print("✓ Empty list test passed")


def test_task_input_model():
    """Test TaskInput model functionality."""
    print("Running test_task_input_model...")
    
    # Test with all fields
    task_with_date = TaskInput(
        title="Test task",
        description="Test description",
        due_date="2025-09-25"
    )
    
    assert task_with_date.title == "Test task"
    assert task_with_date.description == "Test description"
    assert task_with_date.due_date == "2025-09-25"
    
    # Test model_dump functionality
    task_dict = task_with_date.model_dump()
    assert task_dict["title"] == "Test task"
    assert task_dict["description"] == "Test description"
    assert task_dict["due_date"] == "2025-09-25"
    
    # Test without due_date
    task_no_date = TaskInput(
        title="Test task 2",
        description="Test description 2"
    )
    
    assert task_no_date.title == "Test task 2"
    assert task_no_date.due_date is None
    
    print("✓ TaskInput model test passed")


def test_data_transformation():
    """Test that task data is properly transformed before passing to AI service."""
    print("Running test_data_transformation...")
    
    tasks = [
        TaskInput(
            title="Task with special chars & symbols",
            description="Description with (parentheses) and /slashes/",
            due_date="2025-09-30"
        )
    ]

    with patch('app.api.v1.endpoints.ai.summarize_tasks') as mock_summarize:
        mock_summarize.return_value = "Task summary with special characters."
        
        result = summarize_tasks_endpoint(tasks)
        
        # Verify special characters are preserved
        call_args = mock_summarize.call_args[0][0]
        assert "&" in call_args[0]["title"]
        assert "(" in call_args[0]["description"]
        assert "/" in call_args[0]["description"]
        
        print("✓ Data transformation test passed")


def main():
    """Run all tests."""
    print("Starting AI Endpoints Simple Tests")
    print("=" * 45)
    
    try:
        test_summarize_tasks_endpoint_basic()
        test_summarize_tasks_endpoint_error_handling()
        test_summarize_tasks_endpoint_empty_list()
        test_task_input_model()
        test_data_transformation()
        
        print("=" * 45)
        print("✅ All simple endpoint tests passed!")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())