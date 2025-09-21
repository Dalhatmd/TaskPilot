"""
Integration test for AI service - tests actual API calls.
Only runs if GOOGLE_GEMINI_API_KEY is properly configured.
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai_service import summarize_tasks
from app.core.config import settings


def test_real_api_call():
    """Test actual API call to Google Gemini (requires valid API key)."""
    
    # Check if API key is configured
    if not hasattr(settings, 'GOOGLE_GEMINI_API_KEY') or not settings.GOOGLE_GEMINI_API_KEY:
        print("⚠️  GOOGLE_GEMINI_API_KEY not configured - skipping real API test")
        return
    
    print("Running real API test...")
    
    # Sample tasks for testing
    sample_tasks = [
        {
            "id": 1,
            "title": "Complete project proposal",
            "description": "Write and submit the quarterly project proposal by Friday deadline"
        },
        {
            "id": 2,
            "title": "Review code changes",
            "description": "Review pull requests from team members and provide constructive feedback"
        },
        {
            "id": 3,
            "title": "Prepare client presentation",
            "description": "Create slides for Monday client meeting about new features"
        }
    ]
    
    try:
        result = summarize_tasks(sample_tasks)
        
        print("✅ Real API call successful!")
        print("Summary result:")
        print("-" * 40)
        print(result)
        print("-" * 40)
        
        # Basic validation of result
        assert isinstance(result, str)
        assert len(result.strip()) > 0
        print("✓ Result validation passed")
        
    except Exception as e:
        print(f"❌ Real API test failed: {e}")
        raise


def main():
    """Run integration test."""
    print("AI Service Integration Test")
    print("=" * 40)
    
    try:
        test_real_api_call()
        print("=" * 40)
        print("✅ Integration test completed!")
        return 0
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())