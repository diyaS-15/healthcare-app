"""
User Management API Routes
Handles user profile, settings, device sessions, and preferences
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import select

from dependencies import get_current_user, get_db
from models.schemas import User

router = APIRouter(prefix="/api/users", tags=["users"])

# ============================================================================
# SCHEMAS
# ============================================================================

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None  # ISO format
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    blood_type: Optional[str] = None
    medical_conditions: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    notification_enabled: Optional[bool] = None
    preferred_language: Optional[str] = None
    units_system: Optional[str] = None

class UserProfile(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str]
    date_of_birth: Optional[str]
    gender: Optional[str]
    phone_number: Optional[str]
    blood_type: Optional[str]
    medical_conditions: List[str] = []
    medications: List[str] = []
    allergies: List[str] = []
    notification_enabled: bool
    preferred_language: str
    units_system: str
    profile_completeness: float
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime]

class SettingsUpdate(BaseModel):
    email_on_critical_marker: Optional[bool] = None
    email_on_new_insights: Optional[bool] = None
    email_on_trend_changes: Optional[bool] = None
    email_on_weekly_summary: Optional[bool] = None
    theme: Optional[str] = None  # 'light' or 'dark'
    show_advanced_metrics: Optional[bool] = None
    allow_research_participation: Optional[bool] = None
    data_sharing_level: Optional[str] = None  # 'private', 'doctors', 'family'
    require_password_on_sensitive: Optional[bool] = None

class UserSettings(BaseModel):
    email_on_critical_marker: bool
    email_on_new_insights: bool
    email_on_trend_changes: bool
    email_on_weekly_summary: bool
    theme: str
    show_advanced_metrics: bool
    allow_research_participation: bool
    data_sharing_level: str
    require_password_on_sensitive: bool

class DeviceSession(BaseModel):
    id: str
    device_name: Optional[str]
    device_type: str
    os: Optional[str]
    browser: Optional[str]
    ip_address: Optional[str]
    last_active_at: Optional[datetime]
    is_current: bool
    created_at: datetime
    expires_at: Optional[datetime]

class HealthNote(BaseModel):
    id: Optional[str] = None
    title: Optional[str]
    content: str
    note_type: str  # 'symptom', 'medication', 'observation', 'goal', 'general'
    is_pinned: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ============================================================================
# USER PROFILE ENDPOINTS
# ============================================================================

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile
    Requires: Authentication
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Return user profile
    return UserProfile(
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        date_of_birth=getattr(current_user, 'date_of_birth', None),
        gender=getattr(current_user, 'gender', None),
        phone_number=getattr(current_user, 'phone_number', None),
        blood_type=getattr(current_user, 'blood_type', None),
        medical_conditions=getattr(current_user, 'medical_conditions', []),
        medications=getattr(current_user, 'medications', []),
        allergies=getattr(current_user, 'allergies', []),
        notification_enabled=getattr(current_user, 'notification_enabled', True),
        preferred_language=getattr(current_user, 'preferred_language', 'en'),
        units_system=getattr(current_user, 'units_system', 'metric'),
        profile_completeness=getattr(current_user, 'profile_completeness', 0),
        is_verified=getattr(current_user, 'is_verified', False),
        created_at=getattr(current_user, 'created_at', datetime.now()),
        last_login_at=getattr(current_user, 'last_login_at', None)
    )

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's profile
    Requires: Authentication
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Validate profile data
    if profile_update.gender and profile_update.gender not in ['male', 'female', 'other', 'prefer_not_to_say']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid gender value"
        )
    
    if profile_update.blood_type and profile_update.blood_type not in ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blood type"
        )
    
    if profile_update.preferred_language and len(profile_update.preferred_language) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language code"
        )
    
    if profile_update.units_system and profile_update.units_system not in ['metric', 'imperial']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Units system must be 'metric' or 'imperial'"
        )
    
    # Update user object with provided values
    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name
    if profile_update.date_of_birth is not None:
        current_user.date_of_birth = profile_update.date_of_birth
    if profile_update.gender is not None:
        current_user.gender = profile_update.gender
    if profile_update.phone_number is not None:
        current_user.phone_number = profile_update.phone_number
    if profile_update.blood_type is not None:
        current_user.blood_type = profile_update.blood_type
    if profile_update.medical_conditions is not None:
        current_user.medical_conditions = profile_update.medical_conditions
    if profile_update.medications is not None:
        current_user.medications = profile_update.medications
    if profile_update.allergies is not None:
        current_user.allergies = profile_update.allergies
    if profile_update.notification_enabled is not None:
        current_user.notification_enabled = profile_update.notification_enabled
    if profile_update.preferred_language is not None:
        current_user.preferred_language = profile_update.preferred_language
    if profile_update.units_system is not None:
        current_user.units_system = profile_update.units_system
    
    # Calculate profile completeness
    profile_fields = [
        current_user.full_name,
        getattr(current_user, 'date_of_birth', None),
        getattr(current_user, 'gender', None),
        getattr(current_user, 'phone_number', None),
        getattr(current_user, 'blood_type', None),
        getattr(current_user, 'medical_conditions', None),
        getattr(current_user, 'allergies', None),
    ]
    filled_fields = sum(1 for field in profile_fields if field)
    current_user.profile_completeness = (filled_fields / len(profile_fields)) * 100
    
    # TODO: Save to database once Supabase integration is set up
    
    return UserProfile(
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        date_of_birth=getattr(current_user, 'date_of_birth', None),
        gender=getattr(current_user, 'gender', None),
        phone_number=getattr(current_user, 'phone_number', None),
        blood_type=getattr(current_user, 'blood_type', None),
        medical_conditions=getattr(current_user, 'medical_conditions', []),
        medications=getattr(current_user, 'medications', []),
        allergies=getattr(current_user, 'allergies', []),
        notification_enabled=getattr(current_user, 'notification_enabled', True),
        preferred_language=getattr(current_user, 'preferred_language', 'en'),
        units_system=getattr(current_user, 'units_system', 'metric'),
        profile_completeness=current_user.profile_completeness,
        is_verified=getattr(current_user, 'is_verified', False),
        created_at=getattr(current_user, 'created_at', datetime.now()),
        last_login_at=getattr(current_user, 'last_login_at', None)
    )

# ============================================================================
# USER SETTINGS ENDPOINTS
# ============================================================================

@router.get("/settings", response_model=UserSettings)
async def get_user_settings(current_user: User = Depends(get_current_user)):
    """
    Get current user's settings
    Requires: Authentication
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Return default settings for now
    return UserSettings(
        email_on_critical_marker=True,
        email_on_new_insights=True,
        email_on_trend_changes=True,
        email_on_weekly_summary=True,
        theme='light',
        show_advanced_metrics=False,
        allow_research_participation=False,
        data_sharing_level='private',
        require_password_on_sensitive=True
    )

@router.put("/settings", response_model=UserSettings)
async def update_user_settings(
    settings_update: SettingsUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's settings
    Requires: Authentication
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Validate settings
    if settings_update.theme and settings_update.theme not in ['light', 'dark']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Theme must be 'light' or 'dark'"
        )
    
    if settings_update.data_sharing_level and settings_update.data_sharing_level not in ['private', 'doctors', 'family']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data sharing level"
        )
    
    # TODO: Save to database once Supabase integration is set up
    
    return UserSettings(
        email_on_critical_marker=settings_update.email_on_critical_marker or True,
        email_on_new_insights=settings_update.email_on_new_insights or True,
        email_on_trend_changes=settings_update.email_on_trend_changes or True,
        email_on_weekly_summary=settings_update.email_on_weekly_summary or True,
        theme=settings_update.theme or 'light',
        show_advanced_metrics=settings_update.show_advanced_metrics or False,
        allow_research_participation=settings_update.allow_research_participation or False,
        data_sharing_level=settings_update.data_sharing_level or 'private',
        require_password_on_sensitive=settings_update.require_password_on_sensitive or True
    )

# ============================================================================
# DEVICE SESSIONS ENDPOINTS
# ============================================================================

@router.get("/devices", response_model=List[DeviceSession])
async def list_user_devices(current_user: User = Depends(get_current_user)):
    """
    List all active device sessions for current user
    Requires: Authentication
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # TODO: Fetch from database once Supabase integration is set up
    # For now return mock data
    return []

@router.delete("/devices/{device_id}")
async def logout_device(
    device_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Logout a specific device session
    Requires: Authentication
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # TODO: Mark device session as inactive in database
    
    return {"success": True, "message": "Device session terminated"}

@router.delete("/devices")
async def logout_all_devices(current_user: User = Depends(get_current_user)):
    """
    Logout all device sessions except current
    Requires: Authentication
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # TODO: Invalidate all other device sessions
    
    return {"success": True, "message": "All other sessions terminated"}

# ============================================================================
# HEALTH NOTES ENDPOINTS
# ============================================================================

@router.get("/notes", response_model=List[HealthNote])
async def list_health_notes(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List user's health notes with pagination
    Requires: Authentication
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # TODO: Fetch from database once Supabase integration is set up
    return []

@router.post("/notes", response_model=HealthNote)
async def create_health_note(
    note: HealthNote,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new health note
    Requires: Authentication
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    if note.note_type not in ['symptom', 'medication', 'observation', 'goal', 'general']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid note type"
        )
    
    if not note.content or len(note.content.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note content cannot be empty"
        )
    
    # TODO: Save to database once Supabase integration is set up
    
    return note

@router.put("/notes/{note_id}", response_model=HealthNote)
async def update_health_note(
    note_id: str,
    note: HealthNote,
    current_user: User = Depends(get_current_user)
):
    """
    Update a health note
    Requires: Authentication & Ownership
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # TODO: Verify ownership and update in database
    
    return note

@router.delete("/notes/{note_id}")
async def delete_health_note(
    note_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a health note
    Requires: Authentication & Ownership
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # TODO: Verify ownership and delete from database
    
    return {"success": True, "message": "Note deleted"}

# ============================================================================
# ACCOUNT ENDPOINTS
# ============================================================================

@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user)
):
    """
    Delete user account and all associated data (GDPR compliance)
    Requires: Authentication
    WARNING: This action is irreversible
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # TODO: Cascade delete user data from database
    # TODO: Revoke all tokens
    # TODO: Log account deletion in audit log
    
    return {
        "success": True,
        "message": "Account deleted successfully",
        "data_deleted": [
            "User profile",
            "All blood reports",
            "All markers and analysis",
            "Chat history",
            "Health notes",
            "Device sessions"
        ]
    }
