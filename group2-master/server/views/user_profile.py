"""用户个人资料管理模块（从 auth.py 拆分 + 密码修改 + 头像上传）"""

import re

from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from auth_utils import get_auth_error_response, get_request_user
from models import User, db

user_profile_bp = Blueprint('user_profile', __name__)


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def error_response(message='error', code=400, error=''):
    return jsonify({'code': code, 'message': message, 'error': error, 'data': None}), code


def normalize_text(value, max_length=100):
    text = str(value or '').strip()
    if max_length and len(text) > max_length:
        text = text[:max_length]
    return text


EMAIL_REGEX = None


def _get_email_regex():
    import re
    global EMAIL_REGEX
    if EMAIL_REGEX is None:
        EMAIL_REGEX = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', re.I)
    return EMAIL_REGEX


def has_incomplete_zju_domain(email):
    return bool(re.compile(r'@zju\.edu$', re.I).search(email))


def require_user():
    user = get_request_user()
    if not user:
        return None, get_auth_error_response()
    return user, None


@user_profile_bp.route('/api/user/current', methods=['GET'])
def current_user():
    user = get_request_user()
    if not user:
        return get_auth_error_response()
    return success_response(user.to_dict())


@user_profile_bp.route('/api/user/profile', methods=['PUT'])
def update_profile():
    user = get_request_user()
    if not user:
        return get_auth_error_response()

    data = request.get_json() or {}
    requested_id = normalize_text(data.get('id'), 50)
    if requested_id and requested_id != user.id:
        return error_response('用户 ID 不支持修改', 400, 'USER_ID_IMMUTABLE')

    requested_username = normalize_text(data.get('username'), 100)
    if requested_username and requested_username != (user.username or ''):
        return error_response('用户名不支持修改', 400, 'USERNAME_IMMUTABLE')

    name = normalize_text(data.get('name'), 100)
    if not name:
        return error_response('姓名不能为空', 400, 'NAME_REQUIRED')

    email = (data.get('email') or '').strip().lower()
    if email:
        email_regex = _get_email_regex()
        if not email_regex.match(email):
            return error_response('邮箱格式不正确，请检查后重新输入', 400, 'EMAIL_INVALID')
        if has_incomplete_zju_domain(email):
            return error_response('如果使用浙大邮箱，请填写完整的 @zju.edu.cn 后缀', 400, 'EMAIL_DOMAIN_INVALID')
        existing = User.query.filter(User.email == email, User.id != user.id).first()
        if existing:
            return error_response('该邮箱已存在，请更换一个未注册的邮箱', 409, 'EMAIL_ALREADY_EXISTS')

    user.name = name
    user.email = email or user.email
    user.college = normalize_text(data.get('college'), 100) or None
    user.grade = normalize_text(data.get('grade'), 50) or None
    user.campus = normalize_text(data.get('campus'), 100) or None
    user.phone = normalize_text(data.get('phone'), 30) or None

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error_response('个人信息更新失败，请稍后重试', 500, 'PROFILE_UPDATE_FAILED')

    return success_response(user.to_dict(), '个人信息已更新')


@user_profile_bp.route('/api/user/password', methods=['PUT'])
def change_password():
    """修改密码"""
    user, err = require_user()
    if err:
        return err

    data = request.get_json() or {}
    current_password = data.get('currentPassword', '')
    new_password = data.get('newPassword', '')

    if not current_password or not new_password:
        return error_response('请输入当前密码和新密码', 400, 'PASSWORD_REQUIRED')

    if not user.password_hash or not check_password_hash(user.password_hash, current_password):
        return error_response('当前密码不正确', 400, 'BAD_CREDENTIALS')

    if len(new_password) < 8:
        return error_response('密码至少 8 位', 400, 'PASSWORD_TOO_WEAK')
    if not any(c.islower() for c in new_password):
        return error_response('密码需要包含小写字母', 400, 'PASSWORD_TOO_WEAK')
    if not any(c.isupper() for c in new_password):
        return error_response('密码需要包含大写字母', 400, 'PASSWORD_TOO_WEAK')
    if not any(c.isdigit() for c in new_password):
        return error_response('密码需要包含数字', 400, 'PASSWORD_TOO_WEAK')

    user.password_hash = generate_password_hash(new_password)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error_response('密码修改失败，请稍后重试', 500, 'PASSWORD_CHANGE_FAILED')

    return success_response(None, '密码修改成功')


@user_profile_bp.route('/api/user/avatar', methods=['PUT'])
def update_avatar():
    """更新头像URL"""
    user, err = require_user()
    if err:
        return err

    data = request.get_json() or {}
    avatar_url = (data.get('avatar') or '').strip()[:500]

    if not avatar_url:
        return error_response('头像链接不能为空', 400)

    user.avatar = avatar_url

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return error_response('头像更新失败', 500, 'AVATAR_UPDATE_FAILED')

    return success_response(user.to_dict(), '头像更新成功')