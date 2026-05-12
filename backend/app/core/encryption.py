import base64
import os

from cryptography.fernet import Fernet

from app.core.config import get_settings

settings = get_settings()


def _get_fernet() -> Fernet:
    """Devuelve instancia Fernet usando la clave de cifrado configurada."""
    key = settings.ENCRYPTION_KEY
    if not key:
        # Clave de desarrollo (no usar en producción)
        key = base64.urlsafe_b64encode(os.urandom(32)).decode()
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_token(token: str) -> str:
    """Cifra un token OAuth para almacenamiento seguro."""
    f = _get_fernet()
    return f.encrypt(token.encode()).decode()


def decrypt_token(encrypted: str) -> str:
    """Descifra un token OAuth almacenado."""
    f = _get_fernet()
    return f.decrypt(encrypted.encode()).decode()


def encrypt(token: str) -> str:
    """Compatibilidad con la convención BOT-7."""
    return encrypt_token(token)


def decrypt(encrypted: str) -> str:
    """Compatibilidad con la convención BOT-7."""
    return decrypt_token(encrypted)
