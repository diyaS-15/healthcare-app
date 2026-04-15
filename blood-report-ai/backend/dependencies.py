"""
Authentication Dependencies
JWT token validation using Supabase keys.
Add `user: dict = Depends(get_current_user)` to any protected route.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)
bearer = HTTPBearer()


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer)
) -> dict:
    """
    Validate JWT token and return user info.
    Token is signed by Supabase and contains user_id, email, etc.
    """
    token = creds.credentials
    
    try:
        # Decode JWT using Supabase JWT secret
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False}  # Supabase JWTs may not have audience
        )
        
        user_id = payload.get("sub")  # 'sub' is the user ID in Supabase JWTs
        email = payload.get("email", "")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no subject (user_id)",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": user_id,
            "email": email,
            "raw_token": token,
            "payload": payload
        }
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    creds: HTTPAuthorizationCredentials = Depends(bearer) | None = None
) -> dict | None:
    """
    Optional auth — returns user if token provided and valid, None otherwise.
    Use for endpoints that support both public and authenticated access.
    """
    if not creds:
        return None
    try:
        return await get_current_user(creds)
    except HTTPException:
        return None