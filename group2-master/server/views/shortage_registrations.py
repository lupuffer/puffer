from flask import Blueprint, jsonify, request

from auth_utils import get_auth_error_response, get_request_user
from models import ShortageRegistration, db

shortage_registrations_bp = Blueprint('shortage_registrations', __name__)


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def error_response(message='error', code=400, error=''):
    return jsonify({'code': code, 'message': message, 'error': error, 'data': None}), code


def require_user():
    user = get_request_user()
    if not user:
        return None, get_auth_error_response()
    return user, None


def normalize_text(value, max_length):
    text = str(value or '').strip()
    if max_length and len(text) > max_length:
        text = text[:max_length]
    return text


@shortage_registrations_bp.route('/api/shortage-registrations', methods=['GET'])
def get_shortage_registrations():
    user, error = require_user()
    if error:
        return error

    registrations = (
        ShortageRegistration.query
        .filter_by(user_id=user.id)
        .order_by(ShortageRegistration.created_at.desc())
        .all()
    )
    return success_response([item.to_dict() for item in registrations])


@shortage_registrations_bp.route('/api/shortage-registrations', methods=['POST'])
def create_shortage_registration():
    user, error = require_user()
    if error:
        return error

    payload = request.get_json(silent=True) or {}
    book_name = normalize_text(payload.get('bookName'), 200)
    isbn = normalize_text(payload.get('isbn'), 20)
    campus = normalize_text(payload.get('campus'), 100)
    note = normalize_text(payload.get('note'), 500)

    if not book_name:
        return error_response('请输入想登记的书名', 400, 'BOOK_NAME_REQUIRED')

    normalized_isbn = isbn.replace('-', '').replace(' ', '')
    if normalized_isbn and (not normalized_isbn.isdigit() or len(normalized_isbn) not in {10, 13}):
        return error_response('ISBN 需要是 10 位或 13 位数字', 400, 'ISBN_INVALID')

    expected_price = None
    if payload.get('expectedPrice') not in (None, ''):
        try:
            expected_price = round(float(payload.get('expectedPrice')), 2)
        except (TypeError, ValueError):
            return error_response('期望价格格式不正确', 400, 'EXPECTED_PRICE_INVALID')
        if expected_price <= 0:
            return error_response('期望价格需要大于 0', 400, 'EXPECTED_PRICE_INVALID')

    existing = (
        ShortageRegistration.query
        .filter_by(
            user_id=user.id,
            book_name=book_name,
            isbn=normalized_isbn or None,
            campus=campus or None,
            status='waiting',
        )
        .first()
    )
    if existing:
        return success_response(existing.to_dict(), '你已经登记过这本书了')

    registration = ShortageRegistration(
        user_id=user.id,
        book_name=book_name,
        isbn=normalized_isbn or None,
        campus=campus or None,
        expected_price=expected_price,
        note=note or None,
        status='waiting',
    )

    try:
        db.session.add(registration)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return error_response(f'缺货登记保存失败: {exc}', 500, 'SHORTAGE_REGISTRATION_CREATE_FAILED')

    return success_response(registration.to_dict(), '缺货登记成功')


@shortage_registrations_bp.route('/api/shortage-registrations/<int:registration_id>', methods=['DELETE'])
def delete_shortage_registration(registration_id):
    user, error = require_user()
    if error:
        return error

    registration = db.session.get(ShortageRegistration, registration_id)
    if not registration:
        return error_response('缺货登记不存在', 404, 'SHORTAGE_REGISTRATION_NOT_FOUND')
    if registration.user_id != user.id:
        return error_response('没有权限删除这条登记', 403, 'FORBIDDEN')

    try:
        db.session.delete(registration)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return error_response(f'取消缺货登记失败: {exc}', 500, 'SHORTAGE_REGISTRATION_DELETE_FAILED')

    return success_response({'id': registration_id}, '缺货登记已取消')
