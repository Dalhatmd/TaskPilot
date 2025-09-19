"""
Application configuration settings.
Handles environment variables and application settings.
"""

from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
import os
from typing import Any


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Project Information
    PROJECT_NAME: str = "TaskPilot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Configuration
    # Supabase PostgreSQL connection
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    SUPABASE_DB_PASSWORD: Optional[str] = os.getenv("SUPABASE_DB_PASSWORD")
    
    # Database URL - defaults to SQLite for development
    DATABASE_URL: str = "sqlite:///./taskpilot.db"
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        """Assemble database URL from Supabase components if not provided."""
        if isinstance(v, str) and v.startswith("postgresql"):
            return v
        
        # If Supabase credentials are provided, construct PostgreSQL URL
        if values.get("SUPABASE_URL") and values.get("SUPABASE_DB_PASSWORD"):
            supabase_url = values.get("SUPABASE_URL")
            db_password = values.get("SUPABASE_DB_PASSWORD")
            # Extract project reference from Supabase URL
            project_ref = supabase_url.split("//")[1].split(".")[0]
            # URL encode the password to handle special characters
            import urllib.parse
            encoded_password = urllib.parse.quote_plus(db_password)
            return f"postgresql://postgres:{encoded_password}@db.{project_ref}.supabase.co:5432/postgres"
        
        # Default to SQLite for development
        return "sqlite:///./taskpilot.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:8080"
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if v is None:
            return ["http://localhost:3000", "http://localhost:8080"]
        
        if isinstance(v, list):
            return v
        
        if isinstance(v, str):
            # Handle comma-separated string
            if "," in v:
                return [i.strip() for i in v.split(",")]
            # Handle JSON string
            elif v.startswith("["):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    return [v.strip()]
            # Single URL
            else:
                return [v.strip()]
        
        raise ValueError(f"Invalid CORS origins format: {v}")
    
    # AI Integration
    GOOGLE_GEMINI_API_KEY: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# Global settings instance
settings = Settings()
