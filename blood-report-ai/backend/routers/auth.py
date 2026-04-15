"""
Auth Router - User Authentication with Supabase
Sign up, login, token refresh, password change, logout.
"""
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import EmailStr
import logging
from typing import Optional

from models.schemas import SignUpRequest, LoginRequest, AuthResponse, ChangePasswordRequest
from utils.supabase_client import get_supabase
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(req: SignUpRequest):
    """
    Register a new user with Supabase Auth.
    """
    try:
        supabase = get_supabase()
        
        # Create user with Supabase
        auth_response = supabase.auth.sign_up({
            "email": req.email,
            "password": req.password,
            "options": {
                "data": {
                    "full_name": req.full_name
                }
            }
        })
        
        user = auth_response.user
        session = auth_response.session
        
        if not user or not session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signup failed - unable to create user"
            )
        
        logger.info(f"User signed up: {user.email}")
        
        return AuthResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.user_metadata.get("full_name", "") if user.user_metadata else "",
            access_token=session.access_token,
            refresh_token=session.refresh_token,
        )
        
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signup failed: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """
    Login with email and password using Supabase Auth.
    Returns access and refresh tokens.
    """
    try:
        logger.info(f"Login attempt: {req.email}")
        supabase = get_supabase()
        
        # Sign in with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": req.email,
            "password": req.password
        })
        
        user = auth_response.user
        session = auth_response.session
        
        if not user or not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        logger.info(f"User logged in: {user.email}")
        
        return AuthResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.user_metadata.get("full_name", "") if user.user_metadata else "",
            access_token=session.access_token,
            refresh_token=session.refresh_token,
        )
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """
    Refresh an expired access token using the refresh token.
    """
    try:
        logger.info("Token refresh requested")
        supabase = get_supabase()
        
        # Refresh session with Supabase
        auth_response = supabase.auth.refresh_session({
            "refresh_token": refresh_token
        })
        
        session = auth_response.session
        user = auth_response.user
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "expires_in": session.expires_in,
        }
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh token"
        )


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """
    Logout the current user by invalidating their session.
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        supabase = get_supabase()
        
        # Sign out with Supabase
        supabase.auth.sign_out()
        
        logger.info("User logged out")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )


@router.post("/change-password")
async def change_password(req: ChangePasswordRequest, authorization: Optional[str] = Header(None)):
    """
    Change password for the authenticated user.
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        access_token = authorization.replace("Bearer ", "")
        supabase = get_supabase()
        
        # Update user password
        supabase.auth.update_user(
            {"password": req.new_password},
            access_token
        )
        
        logger.info("Password changed successfully")
        
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )


@router.get("/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Get current authenticated user profile.
    """
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        access_token = authorization.replace("Bearer ", "")
        supabase = get_supabase()
        
        # Get user from Supabase
        user = supabase.auth.get_user(access_token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.user_metadata.get("full_name", "") if user.user_metadata else ""
        }
        
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch user"
        )
