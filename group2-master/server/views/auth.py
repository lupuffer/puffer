import uuid
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from auth_utils import (
    AuthError,
    create_token_pair,
    error_response,
    get_auth_error_response,
    get_request_token,
    get_request_user,
    revoke_token,
    validate_token,
)
from models import User, db
from .auth_helpers import (
    EMAIL_REGEX,
    build_payload,
    error_response_short,
    has_incomplete_zju_domain,
    normalize_text,
    parse_remember,
    revoke_if_active,
    success_response,
    validate_email_value,
    validate_password,
)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name:
        return error_response('姓名不能为空', 400, 'NAME_REQUIRED')
    if not username or len(username) < 3:
        return error_response('用户名至少需要 3 个字符', 400, 'USERNAME_TOO_SHORT')
    if not email:
        return error_response('请输入邮箱地址', 400, 'EMAIL_REQUIRED')
    if not EMAIL_REGEX.match(email):
        return error_response('邮箱格式不正确，请检查后重新输入', 400, 'EMAIL_INVALID')
    if has_incomplete_zju_domain(email):
        return error_response('如果使用浙大邮箱，请填写完整的 @zju.edu.cn 后缀', 400, 'EMAIL_DOMAIN_INVALID')
    if not password:
        return error_response('请输入密码', 400, 'PASSWORD_REQUIRED')

    issues = validate_password(password)
    if issues:
        return error_response('密码强度不足，请按要求重新设置', 400, 'PASSWORD_TOO_WEAK', {'requirements': issues})

    if User.query.filter(User.username == username).first():
        return error_response('该用户名已存在，请更换其他用户名', 409, 'USERNAME_ALREADY_EXISTS')
    if User.query.filter(User.email == email).first():
        return error_response('该邮箱已被注册，请直接登录或更换邮箱', 409, 'EMAIL_ALREADY_EXISTS')

    new_user = User(
        id=f'user_{uuid.uuid4().hex[:8]}',
        username=username,
        email=email,
        name=name,
        password_hash=generate_password_hash(password),
        avatar=f'https://api.dicebear.com/7.x/avataaars/svg?seed={username}',
        role='buyer',
        reputation='A',
        created_at=datetime.utcnow(),
    )

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error_response('注册失败，请稍后重试', 500, 'REGISTER_FAILED')

    return success_response(new_user.to_dict(), '注册成功')


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    remember = parse_remember(data.get('rememberMe'))

    if not username or not password:
        return error_response('请输入用户名和密码', 400, 'LOGIN_FIELDS_REQUIRED')

    user = User.query.filter(User.username == username).first()
    if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
        return error_response('用户名或密码错误', 401, 'BAD_CREDENTIALS')

    token_pair = create_token_pair(user, remember_me=remember)
    return success_response(build_payload(user, token_pair), '登录成功')


@auth_bp.route('/api/auth/refresh', methods=['POST'])
def refresh():
    data = request.get_json() or {}
    refresh_token = (data.get('refreshToken') or '').strip()

    if not refresh_token:
        return error_response('缺少刷新凭证，请重新登录', 400, 'REFRESH_TOKEN_REQUIRED')

    try:
        refresh_claims = validate_token(refresh_token, verify_exp=True, expected_type='refresh')
        user = db.session.get(User, refresh_claims['sub'])
        if not user:
            raise AuthError('USER_NOT_FOUND', '用户不存在，请重新登录', 401)
        revoke_if_active(refresh_claims, reason='refresh_rotated')
        token_pair = create_token_pair(user, remember_me=bool(refresh_claims.get('remember')))
    except AuthError as exc:
        return error_response(exc.message, exc.status, exc.error)

    return success_response(build_payload(user, token_pair), '登录状态已刷新')


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    data = request.get_json(silent=True) or {}
    access_token = get_request_token(optional=True)
    refresh_token = (data.get('refreshToken') or '').strip()

    if not access_token and not refresh_token:
        return get_auth_error_response()

    try:
        if access_token:
            revoke_if_active(
                validate_token(access_token, verify_exp=False, expected_type='access'), 'logout'
            )
        if refresh_token:
            revoke_if_active(
                validate_token(refresh_token, verify_exp=False, expected_type='refresh'), 'logout'
            )
    except AuthError as exc:
        return error_response(exc.message, exc.status, exc.error)

    return success_response(None, '退出登录成功')
