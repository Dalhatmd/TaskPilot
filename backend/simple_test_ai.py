"""
Simple test runner for AI service without pytest dependency.
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai_service import summarize_tasks


def test_summarize_tasks_basic():
    """Basic test for task summarization."""
    print("Running test_summarize_tasks_basic...")
    
    # Mock task data
    sample_tasks = [
        {
            "id": 1,
            "title": "Complete project proposal",
            "description": "Write and submit the quarterly project proposal by Friday"
        },
        {
            "id": 2,
            "title": "Review code changes", 
            "description": "Review pull requests and provide feedback to team members"
        }
    ]

    # Mock the genai.GenerativeModel and generate_content response
    mock_response = MagicMock()
    mock_response.text = "Summary: You have 2 main tasks focusing on project completion and code review."

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response

    with patch('app.services.ai_service.genai.GenerativeModel', return_value=mock_model):
        result = summarize_tasks(sample_tasks)
        
        # Basic assertions
        assert result == mock_response.text
        assert "Summary:" in result
        print("✓ Basic functionality test passed")


def test_summarize_tasks_empty():
    """Test with empty task list."""
    print("Running test_summarize_tasks_empty...")
    
    empty_tasks = []
    
    mock_response = MagicMock()
    mock_response.text = "No tasks to summarize."
    
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    
    with patch('app.services.ai_service.genai.GenerativeModel', return_value=mock_model):
        result = summarize_tasks(empty_tasks)
        assert result == "No tasks to summarize."
        print("✓ Empty tasks test passed")


def test_api_call_structure():
    """Test that the API call is structured correctly."""
    print("Running test_api_call_structure...")
    
    tasks = [{"id": 1, "title": "Test Task", "description": "Test Description"}]
    
    mock_response = MagicMock()
    mock_response.text = "Test summary"
    
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    
    with patch('app.services.ai_service.genai.GenerativeModel', return_value=mock_model) as mock_genai:
        summarize_tasks(tasks)
        
        # Verify the model was created with correct model name
        mock_genai.assert_called_once_with("gemini-1.5-flash")
        
        # Verify generate_content was called
        mock_model.generate_content.assert_called_once()
        
        # Check the prompt contains expected elements
        call_args = mock_model.generate_content.call_args[0][0]
        assert "Summarize the following tasks:" in call_args
        assert "Test Task" in call_args
        assert "main objectives" in call_args
        print("✓ API call structure test passed")


def main():
    """Run all tests."""
    print("Starting AI Service Tests")
    print("=" * 40)
    
    try:
        test_summarize_tasks_basic()
        test_summarize_tasks_empty()
        test_api_call_structure()
        
        print("=" * 40)
        print("✅ All tests passed!")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())