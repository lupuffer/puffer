import uuid
from datetime import datetime, timedelta, timezone

from flask import current_app, g, jsonify, request

from jwt_utils import AuthError, _encode_jwt, decode_token
from models import RevokedToken, User, db


def error_response(message, status=400, error='BAD_REQUEST', details=None):
    payload = {
        'code': status,
        'error': error,
        'message': message,
        'data': None,
    }
    if details is not None:
        payload['details'] = details
    return jsonify(payload), status


def get_auth_error_response(default_message='请先登录'):
    auth_error = getattr(g, 'auth_error', None) or AuthError(
        'AUTH_REQUIRED', default_message, 401
    )
    return error_response(auth_error.message, auth_error.status, auth_error.error)


def get_request_token(optional=False):
    authorization = (request.headers.get('Authorization') or '').strip()
    if authorization:
        scheme, _, token = authorization.partition(' ')
        if scheme.lower() != 'bearer' or not token.strip():
            g.auth_error = AuthError(
                'TOKEN_INVALID', '登录凭证格式不正确，请重新登录', 401
            )
            return None
        return token.strip()

    if not optional:
        g.auth_error = AuthError('AUTH_REQUIRED', '请先登录', 401)
    return None


def _create_token(user, token_type, expires_delta, extra_claims=None):
    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta
    claims = {
        'sub': user.id,
        'username': user.username,
        'email': user.email,
        'type': token_type,
        'iss': current_app.config['JWT_ISSUER'],
        'jti': uuid.uuid4().hex,
        'iat': int(now.timestamp()),
        'exp': int(expires_at.timestamp()),
    }
    if extra_claims:
        claims.update(extra_claims)
    return _encode_jwt(claims), expires_at, claims


def create_access_token(user):
    return _create_token(
        user,
        'access',
        timedelta(hours=current_app.config['JWT_ACCESS_TOKEN_EXPIRES_HOURS']),
    )


def create_refresh_token(user, remember_me=False):
    days = current_app.config['JWT_REFRESH_TOKEN_EXPIRES_DAYS']
    if not remember_me or days <= 0:
        return None, None, None
    return _create_token(
        user, 'refresh', timedelta(days=days), {'remember': True}
    )


def create_token_pair(user, remember_me=False):
    access_token, access_expires_at, access_claims = create_access_token(user)
    refresh_token, refresh_expires_at, refresh_claims = create_refresh_token(
        user, remember_me
    )
    return {
        'access_token': access_token,
        'access_expires_at': access_expires_at,
        'access_claims': access_claims,
        'refresh_token': refresh_token or '',
        'refresh_expires_at': refresh_expires_at,
        'refresh_claims': refresh_claims,
        'remember_me': bool(remember_me),
    }


def is_token_revoked(jti):
    if not jti:
        return False
    RevokedToken.query.filter(
        RevokedToken.expires_at <= datetime.utcnow()
    ).delete()
    db.session.commit()
    return RevokedToken.query.filter_by(jti=jti).first() is not None


def validate_token(token, verify_exp=True, expected_type=None):
    claims = decode_token(token, verify_exp, expected_type)
    if is_token_revoked(claims.get('jti')):
        raise AuthError('TOKEN_REVOKED', '登录凭证已失效，请重新登录', 401)
    return claims


def get_request_claims(optional=False, expected_type='access'):
    g.auth_error = None
    token = get_request_token(optional)
    if not token:
        return None
    try:
        g.auth_claims = validate_token(token, True, expected_type)
        return g.auth_claims
    except AuthError as error:
        g.auth_error = error
        return None


def get_request_user(optional=False):
    claims = get_request_claims(optional)
    if claims:
        user = db.session.get(User, claims['sub'])
        if not user:
            g.auth_error = AuthError('USER_NOT_FOUND', '用户不存在，请重新登录', 401)
            return None
        g.auth_user = user
        return user

    if optional:
        return None

    if not getattr(g, 'auth_error', None):
        g.auth_error = AuthError('AUTH_REQUIRED', '请先登录', 401)
    return None


def revoke_token(claims, reason='logout'):
    jti = claims.get('jti')
    subject = claims.get('sub')
    token_type = claims.get('type', 'access')
    if not jti or not subject:
        raise AuthError('TOKEN_INVALID', '登录凭证信息不完整，请重新登录', 401)

    if RevokedToken.query.filter_by(jti=jti).first():
        return

    db.session.add(
        RevokedToken(
            jti=jti,
            user_id=subject,
            token_type=token_type,
            expires_at=datetime.fromtimestamp(
                int(claims['exp']), tz=timezone.utc
            ).replace(tzinfo=None),
            revoked_reason=reason,
        )
    )
    db.session.commit()