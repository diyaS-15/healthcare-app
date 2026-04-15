"""
Pydantic Models - Request/Response Schemas
Complete data schemas for all API endpoints.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

# ━━━━━━━━━━━━━━ AUTH ━━━━━━━━━━━━━━

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int = 3600  # seconds

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ━━━━━━━━━━━━━━ BLOOD MARKERS ━━━━━━━━━━━━━━

class BloodMarkerResponse(BaseModel):
    marker_name: str  # normalized: "hemoglobin"
    display_name: str
    value: float
    unit: str
    reference_min: Optional[float] = None
    reference_max: Optional[float] = None
    status: str  # 'low', 'normal', 'high'

class BloodMarkerSimple(BaseModel):
    """Simple marker for upload parsing"""
    name: str
    value: float
    unit: str

class MarkerValue(BaseModel):
    """Alias for backward compatibility"""
    name: str
    display_name: str
    value: float
    unit: str
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    status: Optional[str] = None


# ━━━━━━━━━━━━━━ BLOOD REPORTS ━━━━━━━━━━━━━━

class BloodReportCreate(BaseModel):
    report_date: str  # "2024-01-10"
    markers: List[BloodMarkerSimple]

class BloodReportResponse(BaseModel):
    id: str
    user_id: str
    report_date: str
    uploaded_at: datetime
    markers: List[BloodMarkerResponse]
    status: str
    file_name: Optional[str] = None

class ReportUploadResponse(BaseModel):
    """Response from report upload"""
    report_id: str
    report_date: date
    marker_count: int
    markers: List[MarkerValue]
    status: str

class ReportHistoryResponse(BaseModel):
    """User's all reports"""
    reports: List[BloodReportResponse]
    total_count: int


# ━━━━━━━━━━━━━━ TRENDS ━━━━━━━━━━━━━━

class TrendPoint(BaseModel):
    date: date
    value: float

class MarkerTrend(BaseModel):
    marker_name: str
    display_name: str
    unit: str
    direction: str  # 'increasing', 'decreasing', 'stable', 'insufficient_data'
    change_percent: float
    consistency: str  # 'gradual', 'rapid', 'fluctuating', 'stable'
    data_points: List[TrendPoint]
    interpretation: Optional[str] = None
    recent_value: Optional[float] = None
    oldest_value: Optional[float] = None

class TrendsResponse(BaseModel):
    trends: List[MarkerTrend]
    cross_marker_patterns: List[str]
    report_count: int
    date_range: dict  # {"from": date, "to": date}
    updated_at: datetime


# ━━━━━━━━━━━━━━ AI ANALYSIS ━━━━━━━━━━━━━━

class AnalysisRequest(BaseModel):
    report_id: str
    simple_mode: bool = False
    user_context: str = ""

class ExplanationResponse(BaseModel):
    """AI explanation of report"""
    summary: str
    marker_details: str
    trends_text: str
    patterns_text: Optional[str] = None
    follow_up_questions: List[str]
    simple_version: Optional[str] = None

class AnalysisResponse(BaseModel):
    summary: str
    marker_details: str
    trends_text: str
    questions: List[str]
    session_id: str


# ━━━━━━━━━━━━━━ CHAT ━━━━━━━━━━━━━━

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatMessageRequest(BaseModel):
    session_id: str
    message: str
    simple_mode: bool = False

class ChatMessageResponse(BaseModel):
    reply: str
    session_id: str
    id: Optional[str] = None
    created_at: Optional[datetime] = None

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    report_id: Optional[str] = None
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime


# ━━━━━━━━━━━━━━ VOICE ━━━━━━━━━━━━━━

class VoiceTranscriptionResponse(BaseModel):
    transcript: str

class VoiceTranscriptRequest(BaseModel):
    audio_base64: str
    language: str = "en"

class VoiceTranscriptResponse(BaseModel):
    text: str
    confidence: Optional[float] = None

class VoiceSynthesisRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    speed: float = 1.0

class VoiceSynthesisResponse(BaseModel):
    audio_base64: str
    mime_type: str = "audio/mpeg"


# ━━━━━━━━━━━━━━ ERRORS ━━━━━━━━━━━━━━

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int


# ━━━━━━━━━━━━━━ ANALYTICS ━━━━━━━━━━━━━━

class PersonalAnalytics(BaseModel):
    """User's personal health analytics"""
    total_reports: int
    markers_tracked: int
    time_period_days: int
    stability_score: float
    marker_trends: List[MarkerTrend]

class GlobalAnalytics(BaseModel):
    """Anonymous global health insights"""
    total_users_analyzed: int
    most_common_markers: List[str]
    average_marker_values: dict
    population_trends: dict
    