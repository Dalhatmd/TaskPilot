#!/usr/bin/env python3
"""
Initialize database with tables and create test user for local development.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from app.core.database import Base, engine
from app.models.user import User
from app.models.task import Task  # Import task model too
from app.core.database import SessionLocal
import uuid

def init_database():
    """Initialize database with tables and test data."""
    
    print("Creating database tables...")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
        
        # Create a test user for local development
        db = SessionLocal()
        
        try:
            # Check if test user already exists
            test_user = db.query(User).filter(User.email == "test@example.com").first()
            
            if not test_user:
                print("Creating test user...")
                test_user = User(
                    email="test@example.com",
                    username="testuser",
                    full_name="Test User",
                    supabase_user_id=str(uuid.uuid4()),
                    is_active=True,
                    is_superuser=False
                )
                
                db.add(test_user)
                db.commit()
                db.refresh(test_user)
                
                print("✓ Test user created successfully")
                print(f"  Email: test@example.com")
                print(f"  Password: Any password works in development mode")
            else:
                print("✓ Test user already exists")
                
        except Exception as e:
            print(f"✗ Failed to create test user: {e}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        print(f"✗ Failed to create database tables: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("Initializing TaskPilot database...")
    success = init_database()
    
    if success:
        print("\n✅ Database initialization completed successfully!")
        print("\nYou can now:")
        print("1. Start the server with: uvicorn app.main:app --reload")
        print("2. Login with test@example.com and any password")
        print("3. Visit http://localhost:8000/docs for API documentation")
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)

