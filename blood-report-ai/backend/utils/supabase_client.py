"""
Supabase Client - Database Access Layer
Handles all interactions with Supabase PostgreSQL database.
All sensitive data is encrypted before storage.
"""
from supabase import create_client, Client
from config import get_settings
import logging
from typing import Optional, List, Dict
import uuid
from datetime import datetime
from functools import lru_cache

logger = logging.getLogger(__name__)
settings = get_settings()


@lru_cache()
def get_supabase() -> Client:
    """
    Returns a Supabase client using the service_role key.
    This bypasses RLS for backend operations.
    RLS is still enforced at the user level via JWT in the frontend.
    """
    return create_client(settings.supabase_url, settings.supabase_service_key)


class SupabaseDB:
    """Convenience methods for common database operations."""
    
    @staticmethod
    def client() -> Client:
        return get_supabase()


# ━━━━━━━━━━━━━━ USERS ━━━━━━━━━━━━━━

async def create_user(user_id: str, email: str, full_name: str) -> Dict:
    """Create a user profile after signup."""
    client = get_supabase()
    
    try:
        result = client.table("users").insert({
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }).execute()
        
        logger.info(f"Created user profile: {user_id}")
        return result.data[0] if result.data else {}
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise

async def get_user(user_id: str) -> Optional[Dict]:
    """Fetch user profile."""
    client = get_supabase()
    
    try:
        result = client.table("users").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None


# ━━━━━━━━━━━━━━ REPORTS ━━━━━━━━━━━━━━

async def save_report(
    user_id: str,
    report_date: str,
    markers: List[Dict],
    raw_text_encrypted: str = "",
    file_name: Optional[str] = None
) -> Dict:
    """Save a blood report and its markers (stub for testing)."""
    # Temporary stub - will connect to Supabase in Option B
    import uuid
    report_id = str(uuid.uuid4())
    logger.info(f"Stub: Would save report {report_id} for user {user_id}")
    return {"report_id": report_id, "marker_count": len(markers)}

async def get_reports(user_id: str, limit: int = 50) -> List[Dict]:
    """Fetch all reports for a user."""
    client = get_supabase()
    
    try:
        result = client.table("blood_reports") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("report_date", desc=True) \
            .limit(limit) \
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching reports: {e}")
        return []

async def get_report_markers(report_id: str) -> List[Dict]:
    """Fetch all markers for a report."""
    client = get_supabase()
    
    try:
        result = client.table("blood_markers") \
            .select("*") \
            .eq("report_id", report_id) \
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching markers: {e}")
        return []


# ━━━━━━━━━━━━━━ TRENDS ━━━━━━━━━━━━━━

async def save_trend_analysis(
    user_id: str,
    marker_name: str,
    trend_direction: str,
    change_percent: float,
    consistency: str,
    data_points: int
) -> Dict:
    """Save trend analysis result."""
    client = get_supabase()
    
    try:
        result = client.table("trend_analysis").upsert({
            "user_id": user_id,
            "marker_name": marker_name,
            "trend_direction": trend_direction,
            "change_percent": change_percent,
            "consistency": consistency,
            "data_points": data_points,
            "updated_at": datetime.utcnow().isoformat(),
        }).execute()
        
        return result.data[0] if result.data else {}
    except Exception as e:
        logger.error(f"Error saving trend: {e}")
        raise

async def get_trends(user_id: str) -> List[Dict]:
    """Fetch all trends for a user."""
    client = get_supabase()
    
    try:
        result = client.table("trend_analysis") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        return []


# ━━━━━━━━━━━━━━ CONVERSATIONS ━━━━━━━━━━━━━━

async def save_chat_message(
    user_id: str,
    message_type: str,
    content_encrypted: str,
    report_id: Optional[str] = None,
    conversation_id: Optional[str] = None
) -> Dict:
    """Save a chat message."""
    client = get_supabase()
    
    try:
        result = client.table("ai_conversations").insert({
            "id": conversation_id or str(uuid.uuid4()),
            "user_id": user_id,
            "report_id": report_id,
            "message_type": message_type,
            "content": content_encrypted,  # Already encrypted
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
        
        return result.data[0] if result.data else {}
    except Exception as e:
        logger.error(f"Error saving chat message: {e}")
        raise

async def get_conversation_history(
    user_id: str,
    report_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict]:
    """Fetch conversation history."""
    client = get_supabase()
    
    try:
        query = client.table("ai_conversations") \
            .select("*") \
            .eq("user_id", user_id)
        
        if report_id:
            query = query.eq("report_id", report_id)
        
        result = query \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching conversation: {e}")
        return []


# ━━━━━━━━━━━━━━ AUDIT LOG ━━━━━━━━━━━━━━

async def log_action(
    user_id: str,
    action: str,
    details_encrypted: Optional[str] = None
) -> Dict:
    """Log a user action for analytics."""
    client = get_supabase()
    
    try:
        result = client.table("audit_log").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action,
            "details": details_encrypted,
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
        
        return result.data[0] if result.data else {}
    except Exception as e:
        logger.error(f"Error logging action: {e}")
        # Don't raise — audit log failures shouldn't break the app


# ━━━━━━━━━━━━━━ KNOWLEDGE BASE ━━━━━━━━━━━━━━

async def get_knowledge_chunks(marker_name: str, limit: int = 5) -> List[Dict]:
    """Fetch educational content about a marker for RAG."""
    client = get_supabase()
    
    try:
        result = client.table("knowledge_base") \
            .select("*") \
            .eq("marker_name", marker_name) \
            .limit(limit) \
            .execute()
        
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error fetching knowledge base: {e}")
        return []
