"""
Voice Service
Speech-to-Text: OpenAI Whisper
Text-to-Speech: ElevenLabs
"""
import httpx
from config import get_settings

settings = get_settings()


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Convert speech audio to text using OpenAI Whisper.
    Accepts: webm, mp3, wav, m4a, ogg, flac
    """
    # Stub - will implement with OpenAI in Option B
    return "Transcribed audio..."


async def synthesize_speech(text: str, voice_id: str = None) -> bytes:
    """
    Convert text to speech using ElevenLabs API.
    Returns raw MP3 audio bytes.
    Falls back to OpenAI TTS if ElevenLabs key not set.
    """
    # Stub - will implement with ElevenLabs in Option B
    return b"audio data..."


async def _elevenlabs_tts(text: str, voice_id: str) -> bytes:
    """ElevenLabs TTS — more natural voices."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": settings.elevenlabs_api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.content


async def _openai_tts(text: str) -> bytes:
    """OpenAI TTS fallback."""
    return b"audio data..."
