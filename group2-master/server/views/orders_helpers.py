from datetime import datetime

from flask import jsonify

from auth_utils import get_auth_error_response, get_request_user
from models import Order

ACTIVE_STATUSES = {'created', 'negotiating', 'confirmed'}


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def error_response(message='error', code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), code


def require_user():
    user = get_request_user()
    if not user:
        return None, get_auth_error_response()
    return user, None


def require_participant(order):
    user, error = require_user()
    if error:
        return None, error
    if order.buyer_id != user.id and order.seller_id != user.id:
        return None, error_response('无权访问该订单', 403)
    return user, None


ALLOWED_STATUS_TRANSITIONS = {
    'created': {'negotiating', 'cancelled'},
    'negotiating': {'created', 'confirmed', 'cancelled'},
    'confirmed': {'completed', 'cancelled'},
}


def get_completion_waiting_message(order, user_id):
    current_role = 'buyer' if order.buyer_id == user_id else 'seller'
    if current_role == 'buyer':
        current_confirmed = bool(order.buyer_completed_confirmed)
        partner_confirmed = bool(order.seller_completed_confirmed)
    else:
        current_confirmed = bool(order.seller_completed_confirmed)
        partner_confirmed = bool(order.buyer_completed_confirmed)

    if current_confirmed and partner_confirmed:
        return '双方已确认，订单已完成'
    if current_confirmed and not partner_confirmed:
        return '你已确认完成，等待对方确认'
    if partner_confirmed and not current_confirmed:
        return '对方已确认完成，等待你确认'
    return '等待双方确认完成'