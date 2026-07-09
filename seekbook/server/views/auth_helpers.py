import re

from flask import jsonify

from models import User

EMAIL_REGEX = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')


def success_response(data=None, message='成功'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def normalize_text(value, max_length):
    text = str(value or '').strip()
    if max_length and len(text) > max_length:
        text = text[:max_length]
    return text


def validate_email_value(email, current_user_id=None):
    normalized_email = normalize_text(email, 255).lower()

    if not normalized_email:
        return None, error_response_short('邮箱不能为空', 400, 'EMAIL_REQUIRED')
    if not EMAIL_REGEX.match(normalized_email):
        return None, error_response_short('邮箱格式不正确，请检查后重新输入', 400, 'EMAIL_INVALID')
    if has_incomplete_zju_domain(normalized_email):
        return None, error_response_short('如果使用浙大邮箱，请填写完整的 @zju.edu.cn 后缀', 400, 'EMAIL_DOMAIN_INVALID')

    existing_user = User.query.filter(
        User.email == normalized_email, User.id != current_user_id
    ).first()
    if existing_user:
        return None, error_response_short(
            '该邮箱已被注册，请更换邮箱', 409, 'EMAIL_ALREADY_EXISTS'
        )

    return normalized_email, None


def error_response_short(message, status=400, error='BAD_REQUEST'):
    return jsonify({'code': status, 'error': error, 'message': message, 'data': None}), status


def validate_password(password):
    issues = []
    if len(password) < 8:
        issues.append('密码长度至少需要 8 位')
    if not re.search(r'[a-z]', password):
        issues.append('密码需要包含至少 1 个小写字母')
    if not re.search(r'[A-Z]', password):
        issues.append('密码需要包含至少 1 个大写字母')
    if not re.search(r'\d', password):
        issues.append('密码需要包含至少 1 个数字')
    return issues


def parse_remember(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}


def has_incomplete_zju_domain(email):
    return email.endswith('@zju.edu')


def build_payload(user, token_pair):
    """构建包含 token 信息的用户响应体"""
    from datetime import timezone
    refresh_exp = token_pair.get('refresh_expires_at')
    return {
        **user.to_dict(),
        'accessToken': token_pair['access_token'],
        'tokenType': 'Bearer',
        'expiresAt': token_pair['access_expires_at'].replace(tzinfo=timezone.utc).isoformat(),
        'refreshToken': token_pair.get('refresh_token') or '',
        'refreshExpiresAt': refresh_exp.replace(tzinfo=timezone.utc).isoformat() if refresh_exp else '',
        'rememberMe': token_pair['remember_me'],
    }


def revoke_if_active(claims, reason):
    """如果 token 未过期则撤销"""
    from datetime import datetime, timezone
    from auth_utils import revoke_token
    exp = int(claims.get('exp', 0))
    if exp > int(datetime.now(timezone.utc).timestamp()):
        revoke_token(claims, reason=reason)
