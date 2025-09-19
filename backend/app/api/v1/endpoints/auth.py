"""
Authentication endpoints.
Handles user registration, login, and profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.auth import UserSignup, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import auth_service
from app.models.user import User

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Creates a new user account with Supabase authentication and stores
    user data in the local database.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        TokenResponse: Access token and user data
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        result = auth_service.signup(user_data, db)
        return TokenResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token.
    
    Validates user credentials with Supabase and returns a JWT token
    for authenticated requests.
    
    Args:
        user_data: User login credentials
        db: Database session
        
    Returns:
        TokenResponse: Access token and user data
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        result = auth_service.login(user_data, db)
        return TokenResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile.
    
    Returns the profile information of the currently authenticated user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user's profile data
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    full_name: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile.
    
    Updates the profile information of the currently authenticated user.
    
    Args:
        full_name: New full name (optional)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserResponse: Updated user profile data
    """
    if full_name is not None:
        current_user.full_name = full_name
        db.commit()
        db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)
