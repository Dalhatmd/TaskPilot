"""
Tests for AI service functionality.
Tests the task summarization feature using Google Generative AI.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.ai_service import summarize_tasks


class TestAIService:
    """Test cases for AI service functions."""

    def test_summarize_tasks_with_valid_input(self):
        """Test task summarization with valid task data."""
        # Mock task data
        sample_tasks = [
            {
                "id": 1,
                "title": "Complete project proposal",
                "description": "Write and submit the quarterly project proposal by Friday",
                "due_date": "2025-09-25"
            },
            {
                "id": 2,
                "title": "Review code changes",
                "description": "Review pull requests and provide feedback to team members",
                "due_date": None
            },
            {
                "id": 3,
                "title": "Prepare presentation",
                "description": "Create slides for client meeting next Monday",
                "due_date": "2025-09-29"
            }
        ]

        # Mock the genai.GenerativeModel and generate_content response
        mock_response = MagicMock()
        mock_response.text = "Summary: You have 3 main tasks focusing on project completion, code review, and client presentation. Key deadline is Friday for the proposal and Monday for the client meeting."

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        with patch('app.services.ai_service.genai.GenerativeModel', return_value=mock_model) as mock_genai:
            result = summarize_tasks(sample_tasks)
            
            # Verify the model was created
            mock_genai.assert_called_once_with("gemini-1.5-flash")
            
            # Verify generate_content was called
            mock_model.generate_content.assert_called_once()
            
            # Check the prompt content
            call_args = mock_model.generate_content.call_args[0][0]
            assert "Complete project proposal" in call_args
            assert "Review code changes" in call_args
            assert "Prepare presentation" in call_args
            
            # Verify the result
            assert result == mock_response.text
            assert "Summary:" in result

    def test_summarize_tasks_with_empty_list(self):
        """Test task summarization with empty task list."""
        empty_tasks = []

        mock_response = MagicMock()
        mock_response.text = "No tasks to summarize."

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        with patch('app.services.ai_service.genai.GenerativeModel', return_value=mock_model) as mock_genai:
            result = summarize_tasks(empty_tasks)
            
            # Verify the model was created
            mock_genai.assert_called_once_with("gemini-1.5-flash")
            
            # Verify generate_content was called
            mock_model.generate_content.assert_called_once()
            
            # Check that the prompt contains empty content
            call_args = mock_model.generate_content.call_args[0][0]
            assert "Summarize the following tasks:" in call_args
            
            # Verify the result
            assert result == "No tasks to summarize."

    def test_summarize_tasks_with_single_task(self):
        """Test task summarization with a single task."""
        single_task = [
            {
                "id": 1,
                "title": "Fix critical bug",
                "description": "Resolve the authentication issue in production ASAP",
                "due_date": "2025-09-22"
            }
        ]

        mock_response = MagicMock()
        mock_response.text = "Critical task: Fix authentication bug in production immediately."

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        with patch('app.services.ai_service.genai.GenerativeModel', return_value=mock_model) as mock_genai:
            result = summarize_tasks(single_task)
            
            # Verify the model was created
            mock_genai.assert_called_once_with("gemini-1.5-flash")
            
            # Verify generate_content was called
            mock_model.generate_content.assert_called_once()
            
            # Check the prompt contains the single task
            call_args = mock_model.generate_content.call_args[0][0]
            assert "Fix critical bug" in call_args
            assert "authentication issue" in call_args
            
            # Verify the result
            assert result == mock_response.text

    def test_summarize_tasks_prompt_structure(self):
        """Test that the prompt is structured correctly."""
        tasks = [
            {"id": 1, "title": "Task 1", "description": "Description 1", "due_date": "2025-09-20"},
            {"id": 2, "title": "Task 2", "description": "Description 2", "due_date": None}
        ]

        mock_response = MagicMock()
        mock_response.text = "Test summary"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        with patch('app.services.ai_service.genai.GenerativeModel', return_value=mock_model) as mock_genai:
            summarize_tasks(tasks)
            
            # Verify the model was created
            mock_genai.assert_called_once_with("gemini-1.5-flash")
            
            # Check prompt structure
            call_args = mock_model.generate_content.call_args[0][0]
            prompt = call_args
            
            # Check prompt structure
            assert "Summarize the following tasks:" in prompt
            assert "1. Task 1: Description 1" in prompt
            assert "2. Task 2: Description 2" in prompt
            assert "main objectives" in prompt
            assert "Deadlines coming up soon" in prompt
            assert "dependencies between tasks" in prompt
            assert "progress overview" in prompt

    @patch('app.services.ai_service.genai.GenerativeModel')
    def test_summarize_tasks_api_error_handling(self, mock_genai_class):
        """Test error handling when AI API fails."""
        tasks = [{"id": 1, "title": "Test Task", "description": "Test Description", "due_date": None}]
        
        # Simulate API error
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API connection failed")
        mock_genai_class.return_value = mock_model
        
        with pytest.raises(Exception) as exc_info:
            summarize_tasks(tasks)
        
        assert "API connection failed" in str(exc_info.value)

    def test_summarize_tasks_with_special_characters(self):
        """Test task summarization with special characters in task data."""
        tasks_with_special_chars = [
            {
                "id": 1,
                "title": "Update API & documentation",
                "description": "Fix API endpoints (v2.0) & update docs with new schema"
            },
            {
                "id": 2,
                "title": "Test: E2E scenarios",
                "description": "Run end-to-end tests for user registration/login flow"
            }
        ]

        mock_response = MagicMock()
        mock_response.text = "Tasks involve API updates and testing procedures."

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        with patch('app.services.ai_service.genai.GenerativeModel', return_value=mock_model) as mock_genai:
            result = summarize_tasks(tasks_with_special_chars)
            
            # Verify special characters are handled properly
            call_args = mock_model.generate_content.call_args[0][0]
            prompt = call_args
            assert "&" in prompt
            assert "(" in prompt
            assert "/" in prompt
            
            assert result == mock_response.text


if __name__ == "__main__":
    # Run tests manually if executed directly
    import sys
    import os
    
    # Add the backend directory to Python path for imports
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    pytest.main([__file__, "-v"])