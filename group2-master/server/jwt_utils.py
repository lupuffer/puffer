import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone

from flask import current_app


class AuthError(Exception):
    def __init__(self, error, message, status=401):
        super().__init__(message)
        self.error = error
        self.message = message
        self.status = status


def _b64url_encode(value):
    return base64.urlsafe_b64encode(value).rstrip(b'=').decode('ascii')


def _b64url_decode(value):
    padding = '=' * (-len(value) % 4)
    return base64.urlsafe_b64decode(f'{value}{padding}'.encode('ascii'))


def _jwt_secret():
    return str(
        current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('SECRET_KEY')
    ).encode('utf-8')


def _encode_jwt(payload):
    header = {'alg': 'HS256', 'typ': 'JWT'}
    header_segment = _b64url_encode(
        json.dumps(header, separators=(',', ':'), sort_keys=True).encode('utf-8')
    )
    payload_segment = _b64url_encode(
        json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')
    )
    signing_input = f'{header_segment}.{payload_segment}'.encode('ascii')
    signature = hmac.new(_jwt_secret(), signing_input, hashlib.sha256).digest()
    return f'{header_segment}.{payload_segment}.{_b64url_encode(signature)}'


def decode_token(token, verify_exp=True, expected_type=None):
    try:
        header_segment, payload_segment, signature_segment = token.split('.')
    except ValueError as exc:
        raise AuthError('TOKEN_INVALID', '登录凭证结构无效，请重新登录', 401) from exc

    try:
        header = json.loads(_b64url_decode(header_segment).decode('utf-8'))
        payload = json.loads(_b64url_decode(payload_segment).decode('utf-8'))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthError('TOKEN_INVALID', '登录凭证解析失败，请重新登录', 401) from exc

    signing_input = f'{header_segment}.{payload_segment}'.encode('ascii')
    expected_sig = _b64url_encode(
        hmac.new(_jwt_secret(), signing_input, hashlib.sha256).digest()
    )
    if not hmac.compare_digest(expected_sig, signature_segment):
        raise AuthError('TOKEN_INVALID', '登录凭证签名无效，请重新登录', 401)

    if header.get('alg') != 'HS256' or header.get('typ') != 'JWT':
        raise AuthError('TOKEN_INVALID', '登录凭证类型不受支持，请重新登录', 401)

    if current_app.config.get('JWT_ISSUER') != payload.get('iss'):
        raise AuthError('TOKEN_INVALID', '登录凭证签发来源无效，请重新登录', 401)

    if expected_type and payload.get('type') != expected_type:
        raise AuthError('TOKEN_INVALID', '登录凭证类型不匹配，请重新登录', 401)

    try:
        exp = int(payload['exp'])
    except (KeyError, TypeError, ValueError) as exc:
        raise AuthError('TOKEN_INVALID', '登录凭证缺少有效过期时间，请重新登录', 401) from exc

    if verify_exp and exp <= int(datetime.now(timezone.utc).timestamp()):
        raise AuthError('TOKEN_EXPIRED', '登录状态已过期，请重新登录', 401)

    if not payload.get('sub') or not payload.get('jti'):
        raise AuthError('TOKEN_INVALID', '登录凭证缺少必要字段，请重新登录', 401)

    return payload