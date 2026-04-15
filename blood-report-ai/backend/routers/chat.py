"""
Chat Router - AI Conversation Endpoints
Free-form chat with context from blood reports.
"""
from fastapi import APIRouter, Depends, HTTPException, status
import logging
import uuid

from dependencies import get_current_user
from models.schemas import ChatMessageRequest, ChatMessageResponse, ChatMessage
from services.llm_brain import general_chat, explain_report, extract_questions_from_response
from services.encryption import encrypt_data, decrypt_data
from utils.supabase_client import save_chat_message, get_conversation_history, get_report_markers
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    req: ChatMessageRequest,
    user: dict = Depends(get_current_user)
):
    """
    Send a message to the AI.
    AI responds with educational information about blood markers.
    """
    try:
        user_id = user["user_id"]
        
        # Get conversation history (encrypted in DB)
        history_encrypted = await get_conversation_history(
            user_id,
            report_id=req.report_id,
            limit=20
        )
        
        # Decrypt history
        history = []
        for msg in history_encrypted:
            try:
                content = decrypt_data(msg["content"], user_id)
            except:
                content = msg["content"]  # Fallback if decryption fails
            
            history.append({
                "role": msg["message_type"],
                "content": content
            })
        
        # Get AI response
        ai_response = general_chat(
            history=history[-10:],  # Last 10 messages for context
            new_message=req.message,
            simple_mode=req.simple_mode
        )
        
        # Encrypt and save messages
        user_msg_encrypted = encrypt_data(req.message, user_id)
        ai_msg_encrypted = encrypt_data(ai_response, user_id)
        
        msg_id = str(uuid.uuid4())
        
        await save_chat_message(
            user_id=user_id,
            message_type="user",
            content_encrypted=user_msg_encrypted,
            report_id=req.report_id,
            conversation_id=msg_id
        )
        
        await save_chat_message(
            user_id=user_id,
            message_type="assistant",
            content_encrypted=ai_msg_encrypted,
            report_id=req.report_id,
            conversation_id=msg_id
        )
        
        return {
            "reply": ai_response,
            "session_id": req.session_id,
            "id": msg_id,
            "created_at": __import__('datetime').datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


@router.get("/history/{session_id}")
async def get_session_history(
    session_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Get conversation history for a session.
    Decrypts messages for the authenticated user.
    """
    try:
        user_id = user["user_id"]
        
        # Fetch encrypted messages
        messages_encrypted = await get_conversation_history(
            user_id,
            report_id=session_id,
            limit=100
        )
        
        # Decrypt
        messages = []
        for msg in messages_encrypted:
            try:
                content = decrypt_data(msg["content"], user_id)
            except:
                content = "[Unable to decrypt]"
            
            messages.append({
                "role": msg["message_type"],
                "content": content,
                "created_at": msg.get("created_at")
            })
        
        return {
            "session_id": session_id,
            "messages": messages,
            "message_count": len(messages)
        }
        
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch conversation history"
        )


@router.post("/ask-simple")
async def ask_simple_explanation(
    marker_name: str,
    user: dict = Depends(get_current_user),
    simple_mode: bool = True
):
    """
    Ask for a simple explanation of a specific marker.
    Simplified "explain like I'm 15" response.
    """
    try:
        from services.normalizer import get_display_name
        
        prompt = f"""
        Explain '{marker_name}' in very simple terms.
        Use everyday analogies and avoid medical jargon.
        Keep it to 2-3 sentences.
        """
        
        response = general_chat(
            history=[],
            new_message=prompt,
            simple_mode=True
        )
        
        return {
            "marker": marker_name,
            "explanation": response,
            "mode": "simple"
        }
        
    except Exception as e:
        logger.error(f"Simple explanation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate explanation"
        )


@router.post("/follow-up")
async def follow_up_question(
    session_id: str,
    context: str,
    user: dict = Depends(get_current_user)
):
    """
    Provide context (lifestyle info) and get updated analysis.
    Example context: "I stopped exercising"
    """
    try:
        user_id = user["user_id"]
        
        # Get recent conversation
        history = await get_conversation_history(
            user_id,
            report_id=session_id,
            limit=5
        )
        
        # Decrypt for context
        recent_response = ""
        if history:
            try:
                recent_response = decrypt_data(history[0]["content"], user_id)
            except:
                pass
        
        # Generate updated response based on context
        follow_up = general_chat(
            history=[{"role": "assistant", "content": recent_response}],
            new_message=f"Here's more context: {context}. Please update your analysis with this.",
            simple_mode=False
        )
        
        # Save follow-up
        context_encrypted = encrypt_data(context, user_id)
        response_encrypted = encrypt_data(follow_up, user_id)
        
        await save_chat_message(
            user_id=user_id,
            message_type="user",
            content_encrypted=context_encrypted,
            report_id=session_id
        )
        
        await save_chat_message(
            user_id=user_id,
            message_type="assistant",
            content_encrypted=response_encrypted,
            report_id=session_id
        )
        
        return {
            "context": context,
            "updated_response": follow_up,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Follow-up error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate follow-up"
        )
