"""
Auth Router - User Authentication
Sign up, login, refresh token, change password.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr
import logging

from models.schemas import SignUpRequest, LoginRequest, AuthResponse, ChangePasswordRequest
from utils.supabase_client import create_user, get_user
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(req: SignUpRequest):
    """
    Register a new user.
    In production, use Supabase Auth API instead of direct signup.
    This is a simplified version.
    """
    try:
        # In production: Use Supabase client auth library
        # auth = supabase.auth.sign_up({
        #     "email": req.email,
        #     "password": req.password
        # })
        
        # For now, return placeholder
        logger.info(f"Signup attempt: {req.email}")
        
        return {
            "user_id": "user_123",
            "email": req.email,
            "full_name": req.full_name,
            "access_token": "token_placeholder",
            "refresh_token": "refresh_placeholder",
        }
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signup failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """
    Login with email and password.
    Returns JWT access token.
    In production: Use Supabase Auth API
    """
    try:
        logger.info(f"Login attempt: {req.email}")
        
        # In production:
        # auth = supabase.auth.sign_in_with_password({
        #     "email": req.email,
        #     "password": req.password
        # })
        # return AuthResponse(
        #     user_id=auth.user.id,
        #     email=auth.user.email,
        #     full_name=auth.user.user_metadata.get("full_name", ""),
        #     access_token=auth.session.access_token,
        #     refresh_token=auth.session.refresh_token,
        # )
        
        return {
            "user_id": "user_123",
            "email": req.email,
            "full_name": "User Name",
            "access_token": "token_placeholder",
            "refresh_token": "refresh_placeholder",
        }
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh an expired access token.
    """
    try:
        # In production: supabase.auth.refresh_session({"refresh_token": refresh_token})
        logger.info("Token refresh requested")
        
        return {
            "access_token": "new_token_placeholder",
            "expires_in": 3600,
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/change-password")
async def change_password(
    user_id: str,
    req: ChangePasswordRequest
):
    """
    Change user password.
    Requires authenticated user.
    """
    try:
        logger.info(f"Password change for user: {user_id}")
        
        # In production:
        # supabase.auth.update_user({
        #     "password": req.new_password
        # })
        
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password change failed"
        )


@router.post("/logout")
async def logout(user_id: str):
    """
    Logout user (invalidate token on frontend).
    Backend doesn't store session state - tokens are stateless.
    """
    logger.info(f"Logout: {user_id}")
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(user_id: str):
    """
    Get current user profile.
    Requires valid JWT token.
    """
    try:
        user = await get_user(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch user"
        )
