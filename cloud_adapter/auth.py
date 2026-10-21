"""High-entropy secret login and bounded, signed HttpOnly sessions. No defaults."""
import hashlib
import hmac
import re
import secrets
import time

COOKIE = '__Host-xpo_session'
TTL = 8 * 60 * 60


def key_valid(key):
    return isinstance(key, str) and 32 <= len(key) <= 512 and len(set(key)) >= 12


def password_matches(supplied, key):
    if not key_valid(key) or not isinstance(supplied, str) or len(supplied) > 512:
        return False
    return hmac.compare_digest(hashlib.sha256(supplied.encode()).digest(), hashlib.sha256(key.encode()).digest())


def issue_session(key, now=None):
    if not key_valid(key):
        raise ValueError('Clave de acceso no configurada')
    now = int(time.time() if now is None else now)
    payload = f'v1.{now + TTL}.{secrets.token_hex(16)}'
    signature = hmac.new(key.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return payload + '.' + signature


def valid_session(value, key, now=None):
    if not key_valid(key) or not isinstance(value, str) or len(value) > 200:
        return False
    match = re.fullmatch(r'(v1\.([0-9]{10})\.[0-9a-f]{32})\.([0-9a-f]{64})', value)
    if not match:
        return False
    now = int(time.time() if now is None else now)
    expiry = int(match[2])
    if not now < expiry <= now + TTL:
        return False
    signature = hmac.new(key.encode(), match[1].encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, match[3])
