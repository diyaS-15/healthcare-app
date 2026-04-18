"""
AES-256-GCM End-to-End Encryption for Medical Data
All blood report markers are encrypted before storing in Supabase.
"""
import os, base64, json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from config import get_settings

settings = get_settings()


def _derive_key(user_id: str) -> bytes:
    """Derive a unique AES-256 key per user using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=user_id.encode(),
        iterations=600_000,  # Increased from 100k for better security
    )
    master_key = bytes.fromhex(settings.encryption_secret)
    return kdf.derive(master_key)


def encrypt_data(data, user_id="default"):
    """Encrypt any data structure with AES-256-GCM."""
    key = _derive_key(user_id)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)

    plaintext = json.dumps(data).encode() if not isinstance(data, str) else data.encode()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    return base64.urlsafe_b64encode(nonce + ciphertext).decode()


def decrypt_data(encrypted, user_id="default"):
    """Decrypt AES-256-GCM encrypted data."""
    key = _derive_key(user_id)
    aesgcm = AESGCM(key)

    combined = base64.urlsafe_b64decode(encrypted.encode())
    nonce, ciphertext = combined[:12], combined[12:]

    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext.decode())