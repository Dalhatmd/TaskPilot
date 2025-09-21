"""
Authentication service using Supabase.
Handles user registration, login, and JWT token management.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from supabase import create_client, Client
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import UserSignup, UserLogin, TokenData


class AuthService:
    """Service for handling authentication with Supabase."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.supabase: Optional[Client] = None
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        
        # Initialize Supabase client if credentials are available
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            except Exception as e:
                print(f"Warning: Failed to initialize Supabase client: {e}")
                self.supabase = None
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        """Verify JWT token and return token data."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: int = payload.get("user_id")
            email: str = payload.get("email")
            
            if user_id is None or email is None:
                raise credentials_exception
            
            return TokenData(user_id=user_id, email=email)
        except JWTError:
            raise credentials_exception
    
    def signup(self, user_data: UserSignup, db: Session) -> Dict[str, Any]:
        """Register a new user with Supabase and create local user record."""
        if not self.supabase:
            # Fallback to local authentication for development
            return self._local_signup(user_data, db)
            
        try:
            # Sign up user with Supabase
            supabase_response = self.supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "username": user_data.username,
                        "full_name": user_data.full_name
                    }
                }
            })
            
            if supabase_response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user account"
                )
            
            # Create local user record
            db_user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                supabase_user_id=supabase_response.user.id,
                is_active=True,
                is_superuser=False
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            # Create access token
            access_token = self.create_access_token(
                data={"user_id": db_user.id, "email": db_user.email}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": db_user
            }
            
        except Exception as e:
            db.rollback()
            if "already registered" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )
    
    def login(self, user_data: UserLogin, db: Session) -> Dict[str, Any]:
        """Authenticate user with Supabase and return access token."""
        if not self.supabase:
            # Fallback to local authentication for development
            return self._local_login(user_data, db)
            
        try:
            # Sign in user with Supabase
            supabase_response = self.supabase.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password
            })
            
            if supabase_response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Get local user record
            db_user = db.query(User).filter(
                User.supabase_user_id == supabase_response.user.id
            ).first()
            
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found in local database"
                )
            
            if not db_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user account"
                )
            
            # Create access token
            access_token = self.create_access_token(
                data={"user_id": db_user.id, "email": db_user.email}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": db_user
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}"
            )
    
    def get_user_by_id(self, user_id: int, db: Session) -> Optional[User]:
        """Get user by ID from database."""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str, db: Session) -> Optional[User]:
        """Get user by email from database."""
        return db.query(User).filter(User.email == email).first()
    
    def _local_signup(self, user_data: UserSignup, db: Session) -> Dict[str, Any]:
        """Local signup for development without Supabase."""
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.email == user_data.email) | (User.username == user_data.username)
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email or username already registered"
                )
            
            # Create local user record with local ID (without Supabase)
            import uuid
            local_user_id = str(uuid.uuid4())  # Generate a local UUID for development
            
            db_user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                supabase_user_id=local_user_id,  # Use local UUID
                is_active=True,
                is_superuser=False
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            # Create access token
            access_token = self.create_access_token(
                data={"user_id": db_user.id, "email": db_user.email}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": db_user
            }
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )
    
    def _local_login(self, user_data: UserLogin, db: Session) -> Dict[str, Any]:
        """Local login for development without Supabase."""
        try:
            # Find user by email
            db_user = db.query(User).filter(User.email == user_data.email).first()
            
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            if not db_user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user account"
                )
            
            # For development, we'll accept any password for simplicity
            # In production, you'd hash and compare passwords properly
            
            # Create access token
            access_token = self.create_access_token(
                data={"user_id": db_user.id, "email": db_user.email}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": db_user
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}"
            )


# Global auth service instance
auth_service = AuthService()
