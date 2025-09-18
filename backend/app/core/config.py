"""
Application configuration settings.
Handles environment variables and application settings.
"""

from typing import List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Project Information
    PROJECT_NAME: str = "TaskPilot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Configuration
    # Supabase PostgreSQL connection
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_DB_PASSWORD: Optional[str] = None
    
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
            return f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"
        
        # Default to SQLite for development
        return "sqlite:///./taskpilot.db"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Alternative frontend port
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
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
