import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from backend.core.conf import settings

_PREFIX = 'enc:v1:'


def _cipher() -> Fernet:
    material = settings.LLM_API_KEY_ENCRYPTION_KEY or settings.TOKEN_SECRET_KEY
    key = base64.urlsafe_b64encode(hashlib.sha256(material.encode('utf-8')).digest())
    return Fernet(key)


def encrypt_secret(value: str) -> str:
    if not value or value.startswith(_PREFIX):
        return value
    token = _cipher().encrypt(value.encode('utf-8')).decode('ascii')
    return f'{_PREFIX}{token}'


def decrypt_secret(value: str) -> str:
    if not value or not value.startswith(_PREFIX):
        return value
    try:
        return _cipher().decrypt(value[len(_PREFIX) :].encode('ascii')).decode('utf-8')
    except InvalidToken as exc:
        raise ValueError('Stored API key cannot be decrypted with the configured key') from exc
