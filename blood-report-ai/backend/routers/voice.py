"""
Voice Router - Voice Chat Endpoints
Speech-to-text: Whisper API
Text-to-speech: ElevenLabs or OpenAI
"""
from fastapi import APIRouter, Depends, HTTPException, status
import logging
import base64

from dependencies import get_current_user
from models.schemas import VoiceTranscriptRequest, VoiceTranscriptResponse, VoiceSynthesisRequest, VoiceSynthesisResponse
from services.voice_service import transcribe_audio, synthesize_speech
from services.llm_brain import general_chat
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


@router.post("/transcribe", response_model=VoiceTranscriptResponse)
async def transcribe(
    req: VoiceTranscriptRequest,
    user: dict = Depends(get_current_user)
):
    """
    Convert speech to text using Whisper API.
    Input: Base64-encoded audio file
    """
    try:
        # Decode audio
        audio_bytes = base64.b64decode(req.audio_base64)
        
        # Transcribe
        transcript = transcribe_audio(audio_bytes, filename="audio.webm")
        
        logger.info(f"Transcribed audio ({len(audio_bytes)} bytes) for user {user['user_id']}")
        
        return {
            "text": transcript,
            "confidence": 0.95  # Whisper doesn't return confidence, placeholder
        }
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to transcribe audio"
        )


@router.post("/synthesize", response_model=VoiceSynthesisResponse)
async def synthesize(
    req: VoiceSynthesisRequest,
    user: dict = Depends(get_current_user)
):
    """
    Convert text to speech.
    returns: Base64-encoded MP3 audio
    """
    try:
        # Synthesize
        audio_bytes = await synthesize_speech(
            text=req.text,
            voice_id=req.voice_id
        )
        
        # Encode to base64
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        logger.info(f"Synthesized {len(req.text)} chars for user {user['user_id']}")
        
        return {
            "audio_base64": audio_base64,
            "mime_type": "audio/mpeg"
        }
        
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to synthesize speech"
        )


@router.post("/chat")
async def voice_chat(
    audio_base64: str,
    user: dict = Depends(get_current_user),
    return_audio: bool = True
):
    """
    Full voice conversation:
    1. Transcribe audio → text
    2. Send to LLM
    3. Synthesize response → audio
    Returns: { "transcript": str, "response": str, "audio": base64 (optional) }
    """
    try:
        user_id = user["user_id"]
        
        # Step 1: Transcribe
        audio_bytes = base64.b64decode(audio_base64)
        user_message = transcribe_audio(audio_bytes, filename="audio.webm")
        
        logger.info(f"Voice message: {user_message[:50]}...")
        
        # Step 2: Get AI response
        ai_response = general_chat(
            history=[],
            new_message=user_message,
            simple_mode=False
        )
        
        # Step 3: Synthesize if requested
        result = {
            "transcript": user_message,
            "response": ai_response,
            "audio": None
        }
        
        if return_audio:
            response_audio = await synthesize_speech(text=ai_response)
            result["audio"] = base64.b64encode(response_audio).decode()
        
        return result
        
    except Exception as e:
        logger.error(f"Voice chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process voice chat"
        )


@router.get("/voices")
async def list_voices(user: dict = Depends(get_current_user)):
    """
    List available TTS voices.
    """
    return {
        "default_voice_id": settings.elevenlabs_voice_id,
        "voices": [
            {"id": "21m00Tcm4TlvDq8ikWAM", "name": "George (Default)", "description": "Male voice"},
            {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Sarah", "description": "Female voice"},
            {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Charlie", "description": "Male voice alt"},
        ],
        "provider": "ElevenLabs"
    }


@router.post("/voice-command")
async def voice_command(
    audio_base64: str,
    command_type: str,
    user: dict = Depends(get_current_user)
):
    """
    Execute a voice command (advanced feature).
    Examples: "analyze the last report", "show trends", etc.
    """
    try:
        # Transcribe
        audio_bytes = base64.b64decode(audio_base64)
        transcript = transcribe_audio(audio_bytes)
        
        logger.info(f"Voice command - type: {command_type}, text: {transcript}")
        
        # Parse command and return appropriate response
        response = f"Command received: {transcript}"
        
        return {
            "command_type": command_type,
            "transcript": transcript,
            "result": response,
            "status": "processed"
        }
        
    except Exception as e:
        logger.error(f"Voice command error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process voice command"
        )
