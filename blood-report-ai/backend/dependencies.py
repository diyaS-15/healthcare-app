"""
Authentication Dependencies
JWT token validation using Supabase (optional).
Supports both authenticated and guest users.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from config import get_settings
import logging
import uuid

settings = get_settings()
logger = logging.getLogger(__name__)
bearer = HTTPBearer(auto_error=False)  # Don't fail if no auth provided


async def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer)
) -> dict:
    """
    Validate JWT token and return user info.
    If no token provided, returns a guest user.
    Allows both authenticated and guest access.
    """
    # If no credentials provided, create a guest user
    if not creds:
        guest_id = str(uuid.uuid4())
        return {
            "user_id": guest_id,
            "email": f"guest-{guest_id[:8]}@guest.local",
            "is_guest": True,
            "raw_token": None,
            "payload": {}
        }
    
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
            "is_guest": False,
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
    creds: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    Optional auth — returns user if token provided and valid, None otherwise.
    Use for endpoints that support both public and authenticated access.
    """
    if not creds:
        return None
    try:
        # Manually call JWT validation since we bypassed auto_error
        token = creds.credentials
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        user_id = payload.get("sub")
        if not user_id:
            return None
        return {
            "user_id": user_id,
            "email": payload.get("email", ""),
            "raw_token": token,
            "payload": payload
        }
    except Exception:
        return None